import http.server
import socketserver
import os
import sys
import json
import re
import glob
from datetime import datetime

PORT = 8000
DIRECTORY = "/workspace/second-brain"

# Load sync script helper functions to reuse logic
sys.path.append(DIRECTORY)
try:
    import logseq_git_sync as sync
except ImportError:
    sync = None

class ApiHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Content-Type")
        self.end_headers()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        if self.path == "/api/status":
            self.send_json({"status": "online", "agent": "Hermes", "sync": "active"})
        elif self.path == "/api/tasks":
            self.handle_get_tasks()
        elif self.path == "/api/projects":
            self.handle_get_projects()
        elif self.path == "/api/goals":
            self.handle_get_goals()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/tasks":
            self.handle_post_task()
        elif self.path == "/api/capture":
            self.handle_post_capture()
        else:
            self.send_error(404, "Endpoint not found")

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def handle_get_tasks(self):
        journals_dir = os.path.join(DIRECTORY, "journals")
        tasks = []
        if not os.path.exists(journals_dir):
            self.send_json([])
            return

        journal_files = glob.glob(os.path.join(journals_dir, "*.md"))
        journal_files.sort(reverse=True)

        todo_pattern = re.compile(r'^\s*-\s+(TODO|DOING)\s+(.*)$')
        timestamped_todo_pattern = re.compile(r'^\s*-\s+\*\*\d{2}:\d{2}\*\*:\s+(TODO|DOING)\s+(.*)$')

        for file_path in journal_files[:5]:
            filename = os.path.basename(file_path)
            date_str = filename.replace(".md", "").replace("_", "-")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    for idx, line in enumerate(f):
                        match = todo_pattern.match(line)
                        if match:
                            status, text = match.groups()
                            tasks.append({
                                "id": f"{date_str}-{idx}",
                                "text": text.strip(),
                                "status": status,
                                "date": date_str
                            })
                            continue
                        
                        match = timestamped_todo_pattern.match(line)
                        if match:
                            status, text = match.groups()
                            tasks.append({
                                "id": f"{date_str}-{idx}",
                                "text": text.strip(),
                                "status": status,
                                "date": date_str
                            })
            except Exception:
                pass
        
        self.send_json(tasks)

    def handle_get_projects(self):
        pages_dir = os.path.join(DIRECTORY, "pages")
        projects = []
        if not os.path.exists(pages_dir):
            self.send_json([])
            return

        page_files = glob.glob(os.path.join(pages_dir, "*.md"))
        for file_path in page_files:
            filename = os.path.basename(file_path)
            page_name = filename.replace(".md", "")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "type:: project" in content or "type:: [[type/project]]" in content:
                        status_match = re.search(r'status::\s*(\S+)', content)
                        status = status_match.group(1).replace("[[", "").replace("]]", "") if status_match else "unknown"
                        desc_match = re.search(r'collapsed::.*\n\t*-\s*(.*)', content)
                        desc = desc_match.group(1) if desc_match else "Logseq Project"
                        projects.append({
                            "name": f"[[project/{page_name}]]",
                            "status": status,
                            "desc": desc,
                            "progress": 40
                        })
            except Exception:
                pass

        self.send_json(projects)

    def handle_get_goals(self):
        pages_dir = os.path.join(DIRECTORY, "pages")
        goals = []
        if not os.path.exists(pages_dir):
            self.send_json([])
            return

        page_files = glob.glob(os.path.join(pages_dir, "*.md"))
        for file_path in page_files:
            filename = os.path.basename(file_path)
            page_name = filename.replace(".md", "")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "type:: goal" in content or "type:: [[type/goal]]" in content:
                        goals.append({
                            "name": f"[[goal/{page_name}]]",
                            "status": "active"
                        })
            except Exception:
                pass

        self.send_json(goals)

    def handle_post_task(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(post_data)
            task_text = data.get("text", "")
            if not task_text:
                self.send_json({"error": "Empty text"}, 400)
                return

            if sync:
                config = sync.load_config()
                success, msg = sync.append_to_journal(config, task_text)
                self.send_json({"success": success, "message": msg})
            else:
                self.send_json({"error": "Sync module unavailable"}, 500)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def handle_post_capture(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            data = json.loads(post_data)
            capture_text = data.get("text", "")
            if not capture_text:
                self.send_json({"error": "Empty text"}, 400)
                return

            if sync:
                config = sync.load_config()
                success, msg = sync.append_to_journal(config, f"{capture_text} #inbox")
                self.send_json({"success": success, "message": msg})
            else:
                self.send_json({"error": "Sync module unavailable"}, 500)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

def start_server():
    global PORT
    for attempt in range(5):
        try:
            handler = ApiHandler
            with socketserver.TCPServer(("", PORT), handler) as httpd:
                print(f"SERVING: Port {PORT} from directory {DIRECTORY}")
                sys.stdout.flush()
                httpd.serve_forever()
        except OSError as e:
            print(f"Port {PORT} bound or failed: {e}. Trying next port...")
            sys.stdout.flush()
            PORT += 1
