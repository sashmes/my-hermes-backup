In cloud hosting environments, YouTube blocks direct scraping requests from the VM's IP address (e.g., with bot-detection or LOGIN_REQUIRED messages). To bypass this, route transcript scraping requests through public proxies using a fast global timeout (e.g., socket.setdefaulttimeout(3.0)) to avoid hanging. This has been integrated directly as a fallback into the youtube-content skill.
§
The Logseq second brain is located at `/workspace/second-brain` and synchronized with the private GitHub repository `https://github.com/sashmes/second-brain` on branch `main` using the automated `logseq_git_sync.py` script.
§
User has a Logseq "second brain" repository initialized at /workspace/second-brain tracking remote https://github.com/sashmes/second-brain on branch main. Timezone is America/New_York. Notes are written in Logseq outliner style (bullets starting with "- "). Sync is handled via logseq_git_sync.py and search via logseq_search.py.
§
User has planned an "Agentic Life Operating System" (@LOS) based on August Bradley's Pillars, Pipelines, and Vaults (PPV) framework, adapted to Logseq. The build is on hold and will be resumed in a day or two. The plan involves creating templates in pages/Templates.md, constructing pages/Life_OS_Dashboard.md with advanced Logseq queries, and enabling Hermes smart-inbox features.
§
User's local Logseq vault path on their laptop is `/home/lowxprt/thoughts`. Always automatically draft, generate, and populate a structured 'Summary [AI Generated]' block whenever adding/ingesting a new resource, reading, or bookmark.