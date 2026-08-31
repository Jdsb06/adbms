import os
import re
import subprocess

def escape_latex(text):
    """Escapes special LaTeX characters in plain text while preserving TeX commands and math."""
    # Split text into math segments ($...$ or $$...$$) and plain text
    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', text, flags=re.DOTALL)
    res = []
    for p in parts:
        if p.startswith('$') and p.endswith('$'):
            # Math block - preserve math
            # Replace unescaped % inside math if any
            m = p
            res.append(m)
        else:
            s = p
            s = s.replace('&', r'\&')
            s = s.replace('%', r'\%')
            s = s.replace('#', r'\#')
            s = s.replace('_', r'\_')
            res.append(s)
    return ''.join(res)

def md_to_tex(md_file, tex_file):
    with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.splitlines()
    tex_out = []

    tex_out.append(r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=0.85in]{geometry}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{float}
\usepackage{enumitem}

\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    urlcolor=blue,
    citecolor=blue
}

\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    backgroundcolor=\color{gray!10},
    frame=single,
    framerule=0.5pt,
    rulecolor=\color{gray!30},
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{green!60!black},
    stringstyle=\color{orange}
}

\title{\textbf{Advanced Database Management Systems (ADBMS)}\\[0.5em] \Large Assignment 0 \& Assignment 1: Histogram Analysis Report}
\author{\textbf{IIIT Bangalore}}
\date{\today}

\begin{document}
\maketitle
\tableofcontents
\newpage
''')

    in_code = False
    code_lines = []
    in_table = False
    table_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Handle Code blocks
        if stripped.startswith('```'):
            if in_code:
                code_text = '\n'.join(code_lines)
                tex_out.append(r'\begin{lstlisting}' + '\n' + code_text + '\n' + r'\end{lstlisting}' + '\n')
                code_lines = []
                in_code = False
            else:
                in_code = True
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        # Handle HTML comment lines
        if stripped.startswith('<!--') and stripped.endswith('-->'):
            continue

        # Handle Markdown Tables
        if stripped.startswith('|') and stripped.endswith('|'):
            table_lines.append(stripped)
            in_table = True
            continue
        elif in_table:
            if table_lines:
                rows = []
                for tline in table_lines:
                    cols = [c.strip() for c in tline.split('|')[1:-1]]
                    rows.append(cols)

                if len(rows) > 1 and all(set(c) <= set(':- ') for c in rows[1]):
                    header = rows[0]
                    body = rows[2:]
                else:
                    header = rows[0]
                    body = rows[1:]

                num_cols = len(header)
                col_spec = ' | '.join(['X' if i == len(header)-1 or i == 1 else 'l' for i in range(num_cols)])
                
                tex_out.append(r'\begin{table}[H]' + '\n' + r'\centering' + '\n' + r'\small' + '\n')
                tex_out.append(r'\begin{tabularx}{\textwidth}{' + col_spec + r'}' + '\n' + r'\toprule' + '\n')
                
                header_cells = []
                for h in header:
                    h_text = escape_latex(h)
                    h_text = re.sub(r'`(.*?)`', r'\\texttt{\1}', h_text)
                    header_cells.append(r'\textbf{' + h_text + '}')
                header_str = ' & '.join(header_cells) + r' \\' + '\n' + r'\midrule' + '\n'
                tex_out.append(header_str)

                for row in body:
                    row_cells = []
                    for cell in row:
                        c_text = escape_latex(cell)
                        c_text = re.sub(r'`(.*?)`', r'\\texttt{\1}', c_text)
                        row_cells.append(c_text)
                    row_str = ' & '.join(row_cells) + r' \\' + '\n'
                    tex_out.append(row_str)

                tex_out.append(r'\bottomrule' + '\n' + r'\end{tabularx}' + '\n' + r'\end{table}' + '\n')
                table_lines = []
                in_table = False

        # Handle Images
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            alt_text = escape_latex(img_match.group(1))
            img_rel_path = img_match.group(2)
            img_path = img_rel_path.replace('../plots/', '../plots/').replace('plots/', '../plots/')
            if not img_path.startswith('../'):
                img_path = '../' + img_path
                
            tex_out.append(r'\begin{figure}[H]' + '\n' + r'\centering' + '\n')
            tex_out.append(r'\includegraphics[width=0.85\textwidth]{' + img_path + r'}' + '\n')
            tex_out.append(r'\caption{' + alt_text + r'}' + '\n')
            tex_out.append(r'\end{figure}' + '\n')
            continue

        # Handle Headings
        if stripped.startswith('# '):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            tex_out.append(r'\section{' + escape_latex(stripped[2:]) + r'}' + '\n')
            continue
        elif stripped.startswith('## '):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            tex_out.append(r'\subsection{' + escape_latex(stripped[4:]) + r'}' + '\n')
            continue
        elif stripped.startswith('### '):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            tex_out.append(r'\subsubsection{' + escape_latex(stripped[5:]) + r'}' + '\n')
            continue
        elif stripped.startswith('#### '):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            tex_out.append(r'\paragraph{' + escape_latex(stripped[6:]) + r'}' + '\n')
            continue

        # Handle Lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                tex_out.append(r'\begin{itemize}' + '\n')
                in_list = True
            item_text = escape_latex(stripped[2:])
            item_text = re.sub(r'`(.*?)`', r'\\texttt{\1}', item_text)
            item_text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', item_text)
            tex_out.append(r'\item ' + item_text + '\n')
            continue
        elif in_list and not stripped:
            tex_out.append(r'\end{itemize}' + '\n')
            in_list = False

        if not stripped:
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            tex_out.append('\n')
            continue

        # Horizontal Rule
        if stripped == '---':
            tex_out.append(r'\hrule' + '\n\n')
            continue

        # Paragraph text
        para_text = escape_latex(stripped)
        para_text = re.sub(r'`(.*?)`', r'\\texttt{\1}', para_text)
        para_text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', para_text)
        tex_out.append(para_text + '\n\n')

    if in_list:
        tex_out.append(r'\end{itemize}' + '\n')

    tex_out.append(r'\end{document}' + '\n')

    full_tex = ''.join(tex_out)
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(full_tex)

    print(f"Generated {tex_file} from {md_file}")

def compile_pdf(tex_file):
    tex_dir = os.path.dirname(os.path.abspath(tex_file))
    tex_base = os.path.basename(tex_file)
    print(f"Compiling {tex_base} with pdflatex in {tex_dir}...")
    
    subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_base], cwd=tex_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cmd = subprocess.run(['pdflatex', '-interaction=nonstopmode', tex_base], cwd=tex_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    pdf_file = tex_file.replace('.tex', '.pdf')
    if os.path.exists(pdf_file):
        print(f"Successfully compiled PDF: {pdf_file}")
    else:
        print(f"Error compiling PDF for {tex_file}. Check LaTeX log.")
        stdout_str = cmd.stdout.decode('utf-8', errors='replace')
        print(stdout_str[-800:])

if __name__ == '__main__':
    md_path = 'reports/Assignment_Report.md'
    tex_path = 'reports/Assignment_Report.tex'
    md_to_tex(md_path, tex_path)
    compile_pdf(tex_path)

    llm_md = 'reports/LLM_Conversations.md'
    llm_tex = 'reports/LLM_Conversations.tex'
    if os.path.exists(llm_md):
        md_to_tex(llm_md, llm_tex)
        compile_pdf(llm_tex)
