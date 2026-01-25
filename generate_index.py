import os
import json
import html

# Configuration
ROOT_DIR = r"d:\projects_2\AI_vibe_code_antigravity\interview_prep"
OUTPUT_FILE = os.path.join(ROOT_DIR, "index.html")
IGNORE_DIRS = {".git", ".idea", "__pycache__", "venv", "node_modules", ".gemini"}
IGNORE_FILES = {"index.html", "generate_index.py"}

def get_file_tree(start_path):
    tree = {"name": os.path.basename(start_path), "type": "directory", "children": []}
    
    try:
        items = sorted(os.listdir(start_path))
    except PermissionError:
        return None

    for item in items:
        path = os.path.join(start_path, item)
        
        if item in IGNORE_FILES:
            continue
            
        if os.path.isdir(path):
            if item in IGNORE_DIRS:
                continue
            child_node = get_file_tree(path)
            if child_node:
                tree["children"].append(child_node)
        else:
            if item.lower().endswith(".md"):
                try:
                    with open(path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    tree["children"].append({
                        "name": item,
                        "type": "file",
                        "content": content
                    })
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    
    return tree

def generate_html(data):
    json_data = json.dumps(data)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Prep Notes</title>
    <!-- GitHub Markdown CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.2.0/github-markdown.min.css">
    <!-- Marked.js for Markdown rendering -->
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {{
            --bg-color: #ffffff;
            --text-color: #24292f;
            --sidebar-bg: #f6f8fa;
            --sidebar-border: #d0d7de;
            --link-color: #0969da;
            --markdown-bg: #ffffff;
            --markdown-text: #24292f;
        }}

        [data-theme="dark"] {{
            --bg-color: #0d1117;
            --text-color: #c9d1d9;
            --sidebar-bg: #161b22;
            --sidebar-border: #30363d;
            --link-color: #58a6ff;
            --markdown-bg: #0d1117;
            --markdown-text: #c9d1d9;
        }}

        body {{
            margin: 0;
            display: flex;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            overflow: hidden;
            background-color: var(--bg-color);
            color: var(--text-color);
            transition: background-color 0.3s, color 0.3s;
        }}
        
        #sidebar {{
            width: 300px;
            background-color: var(--sidebar-bg);
            border-right: 1px solid var(--sidebar-border);
            overflow-y: auto;
            padding: 20px;
            flex-shrink: 0;
            transition: transform 0.3s ease, width 0.3s ease;
        }}
        
        #content {{
            flex-grow: 1;
            padding: 40px;
            overflow-y: auto;
            background-color: var(--markdown-bg);
            position: relative;
        }}

        /* Zen Mode: Hide Sidebar */
        body.zen-mode #sidebar {{
            width: 0;
            padding: 0;
            border: none;
            overflow: hidden;
            transform: translateX(-100%);
        }}

        body.zen-mode #content {{
            padding: 40px 15%; /* Center content more in Zen Mode */
        }}

        /* Markdown Dark Mode Overrides */
        [data-theme="dark"] .markdown-body {{
            color-scheme: dark;
            --color-canvas-default: #0d1117;
            --color-canvas-subtle: #161b22;
            --color-border-default: #30363d;
            --color-border-muted: #21262d;
            --color-fg-default: #c9d1d9;
            --color-fg-muted: #8b949e;
            --color-accent-fg: #58a6ff;
            /* Add more GitHub Dark variables as needed */
        }}

        .markdown-body {{
            box-sizing: border-box;
            min-width: 200px;
            max-width: 980px;
            margin: 0 auto;
            padding: 45px;
            background-color: transparent !important; /* Let body bg show through */
        }}

        @media (max-width: 767px) {{
            .markdown-body {{
                padding: 15px;
            }}
            #sidebar {{
                width: 100%;
                height: 30%;
                border-right: none;
                border-bottom: 1px solid var(--sidebar-border);
                transform: none !important; /* Disable Zen transformation on mobile for now */
            }}
            body {{
                flex-direction: column;
            }}
            body.zen-mode #sidebar {{
                height: 0;
                padding: 0;
            }}
        }}
        
        /* Tree View Styles */
        ul {{
            list-style-type: none;
            padding-left: 20px;
            margin: 0;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        .folder-name {{
            font-weight: bold;
            cursor: pointer;
            color: var(--text-color);
            display: flex;
            align-items: center;
        }}
        
        .folder-name::before {{
            content: '📂';
            margin-right: 5px;
        }}

        .file-link {{
            cursor: pointer;
            color: var(--link-color);
            text-decoration: none;
            display: flex;
            align-items: center;
        }}
        
        .file-link:hover {{
            text-decoration: underline;
        }}
        
        .file-link::before {{
            content: '📄';
            margin-right: 5px;
        }}

        .folder-content {{
            display: none;
        }}
        
        .folder-open > .folder-content {{
            display: block;
        }}
        
        /* Toolbar */
        .toolbar {{
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            justify-content: space-between;
        }}
        
        button {{
            padding: 5px 10px;
            cursor: pointer;
            border-radius: 6px;
            border: 1px solid var(--sidebar-border);
            background-color: var(--bg-color);
            color: var(--text-color);
        }}

        button:hover {{
            opacity: 0.8;
        }}

        /* Floating Zen Toggle (Visible only when sidebar is hidden) */
        #zen-toggle-floating {{
            position: fixed;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            display: none;
            background: var(--sidebar-bg);
            border: 1px solid var(--sidebar-border);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 20px;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            padding: 0;
        }}

        body.zen-mode #zen-toggle-floating {{
            display: flex;
        }}

    </style>
</head>
<body>

<!-- Floating button to exit Zen Mode -->
<button id="zen-toggle-floating" title="Exit Zen Mode">👁️</button>

<div id="sidebar">
    <div class="toolbar">
        <button id="theme-toggle" title="Toggle Dark/Light Mode">🌙</button>
        <button id="zen-toggle-sidebar" title="Enter Zen Mode">▣</button>
    </div>
    <h3>📚 Knowledge Base</h3>
    <div id="tree-root"></div>
</div>

<div id="content">
    <div id="markdown-viewer" class="markdown-body">
        <h1>Select a file to view</h1>
        <p>Click on any file in the sidebar to load its content.</p>
    </div>
</div>

<script>
    const fileData = {json_data};

    // --- functionalities ---
    
    // Theme logic
    const themeBtn = document.getElementById('theme-toggle');
    const storedTheme = localStorage.getItem('theme') || 'light';
    if (storedTheme === 'dark') {{
        document.documentElement.setAttribute('data-theme', 'dark');
        themeBtn.textContent = '☀️';
    }}

    themeBtn.onclick = () => {{
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        themeBtn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }};

    // Zen Mode logic
    const zenBtns = [document.getElementById('zen-toggle-sidebar'), document.getElementById('zen-toggle-floating')];
    const isZen = localStorage.getItem('zenMode') === 'true';
    if (isZen) {{
        document.body.classList.add('zen-mode');
    }}

    zenBtns.forEach(btn => {{
        btn.onclick = () => {{
            document.body.classList.toggle('zen-mode');
            localStorage.setItem('zenMode', document.body.classList.contains('zen-mode'));
        }};
    }});

    // Rendering logic
    function renderTree(node, container) {{
        const ul = document.createElement('ul');
        
        if (node.children) {{
            node.children.forEach(child => {{
                const li = document.createElement('li');
                
                if (child.type === 'directory') {{
                    if (child.children.length === 0) return;

                    const folderDiv = document.createElement('div');
                    folderDiv.className = 'folder-node';
                    
                    const span = document.createElement('span');
                    span.className = 'folder-name';
                    span.textContent = child.name;
                    span.onclick = function(e) {{
                        e.stopPropagation();
                        folderDiv.classList.toggle('folder-open');
                    }};
                    
                    folderDiv.appendChild(span);
                    
                    const contentDiv = document.createElement('div');
                    contentDiv.className = 'folder-content';
                    renderTree(child, contentDiv);
                    folderDiv.appendChild(contentDiv);
                    
                    li.appendChild(folderDiv);
                }} else {{
                    const a = document.createElement('a');
                    a.className = 'file-link';
                    a.textContent = child.name;
                    a.onclick = function(e) {{
                        e.preventDefault();
                        displayContent(child.content);
                        document.querySelectorAll('.file-link').forEach(el => el.style.fontWeight = 'normal');
                        a.style.fontWeight = 'bold';
                    }};
                    li.appendChild(a);
                }}
                
                ul.appendChild(li);
            }});
        }}
        
        container.appendChild(ul);
    }}

    function displayContent(markdown) {{
        const viewer = document.getElementById('markdown-viewer');
        viewer.innerHTML = marked.parse(markdown);
    }}

    const rootContainer = document.getElementById('tree-root');
    renderTree(fileData, rootContainer);
    // Auto-open top level folders (Disabled by default)
    // document.querySelectorAll('.folder-node').forEach(el => el.classList.add('folder-open'));

</script>

</body>
</html>
"""
    return html_content

def main():
    print("Scanning directory...")
    tree = get_file_tree(ROOT_DIR)
    
    print("Generating HTML...")
    html_output = generate_html(tree)
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_output)
    
    print(f"Success! Index generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
