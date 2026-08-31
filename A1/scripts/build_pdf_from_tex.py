import os
import re
import subprocess

def fix_math_subscripts(text):
    """Fix math subscript notations."""
    text = re.sub(r'S_\{+act\}+', r'S_{\\text{act}}', text)
    text = re.sub(r'S_\{+est\}+', r'S_{\\text{est}}', text)
    return text

def process_inline(text, escape_all_backslash=False):
    """Escapes special LaTeX characters in plain text while preserving LaTeX math and inline formatting."""
    text = fix_math_subscripts(text)
    
    if escape_all_backslash:
        s = text
        s = s.replace('\\', r'\textbackslash{}')
        s = s.replace('&', r'\&')
        s = s.replace('%', r'\%')
        s = s.replace('#', r'\#')
        s = s.replace('_', r'\_')
        s = s.replace('~', r'\textasciitilde{}')
        s = s.replace('^', r'\textasciicircum{}')
        s = re.sub(r'`(.*?)`', r'\\texttt{\1}', s)
        s = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', s)
        return s

    parts = re.split(r'(\$\$.*?\$\$|\$.*?\$)', text, flags=re.DOTALL)
    res = []
    for p in parts:
        if p.startswith('$') and p.endswith('$'):
            m = p
            m = re.sub(r'(?<!\\)%', r'\%', m)
            res.append(m)
        else:
            s = p
            s = s.replace('\\', r'\textbackslash{}')
            s = s.replace('&', r'\&')
            s = s.replace('%', r'\%')
            s = s.replace('#', r'\#')
            s = s.replace('_', r'\_')
            s = s.replace('~', r'\textasciitilde{}')
            s = s.replace('^', r'\textasciicircum{}')
            s = re.sub(r'`(.*?)`', r'\\texttt{\1}', s)
            s = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', s)
            res.append(s)
    return ''.join(res)

def clean_table_line(tline):
    # Replace pipes inside math expressions $...$ or escaped \| with \vert before splitting row by |
    def replace_math_pipe(m):
        return m.group(0).replace('|', r'\vert ')
    tline = re.sub(r'\$.*?\$', replace_math_pipe, tline)
    tline = tline.replace(r'\|', r'\vert ')
    return tline

def md_to_tex(md_file, tex_file, is_log_file=False):
    with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    lines = content.splitlines()
    tex_out = []

    doc_title = "ADBMS LLM Conversation Log" if is_log_file else "Advanced Database Management Systems (ADBMS)\\\\[0.5em] \\Large Assignment 0 \\& Assignment 1: Histogram Analysis Report"

    tex_out.append(r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[margin=0.85in]{geometry}
\usepackage{amsmath,amssymb,amsfonts}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{tabularx}
\usepackage{xltabular}
\usepackage{hyperref}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{float}
\usepackage{enumitem}

\graphicspath{{../plots/}{./plots/}{plots/}}

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

\title{\textbf{''' + doc_title + r'''}}
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

        # Code blocks
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

        # HTML comments
        if stripped.startswith('<!--') and stripped.endswith('-->'):
            continue

        # Markdown Tables
        if stripped.startswith('|') and stripped.endswith('|'):
            table_lines.append(stripped)
            in_table = True
            continue
        elif in_table:
            if table_lines:
                rows = []
                for tline in table_lines:
                    tline_clean = clean_table_line(tline)
                    cols = [c.strip() for c in tline_clean.split('|')[1:-1]]
                    rows.append(cols)

                if len(rows) > 1 and all(set(c) <= set(':- ') for c in rows[1]):
                    header = rows[0]
                    body = rows[2:]
                else:
                    header = rows[0]
                    body = rows[1:]

                num_cols = len(header)
                col_spec = ' | '.join(['X' if i == len(header)-1 or i == 1 else 'l' for i in range(num_cols)])
                
                tex_out.append(r'\small' + '\n')
                tex_out.append(r'\begin{xltabular}{\textwidth}{' + col_spec + r'}' + '\n')
                tex_out.append(r'\toprule' + '\n')
                
                header_cells = [r'\textbf{' + process_inline(h, is_log_file) + '}' for h in header]
                header_str = ' & '.join(header_cells) + r' \\' + '\n' + r'\midrule' + '\n' + r'\endfirsthead' + '\n'
                tex_out.append(header_str)

                tex_out.append(r'\toprule' + '\n' + header_str + r'\endhead' + '\n')
                tex_out.append(r'\bottomrule' + '\n' + r'\endfoot' + '\n')
                tex_out.append(r'\bottomrule' + '\n' + r'\endlastfoot' + '\n')

                for row in body:
                    row_cells = [process_inline(cell, is_log_file) for cell in row]
                    row_str = ' & '.join(row_cells) + r' \\' + '\n'
                    tex_out.append(row_str)

                tex_out.append(r'\end{xltabular}' + '\n\n')
                table_lines = []
                in_table = False

        # Images
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)', stripped)
        if img_match:
            alt_text = process_inline(img_match.group(1), is_log_file)
            img_rel_path = img_match.group(2)
            filename = os.path.basename(img_rel_path)
            
            tex_out.append(r'\begin{figure}[H]' + '\n' + r'\centering' + '\n')
            tex_out.append(r'\includegraphics[width=0.85\textwidth]{' + filename + r'}' + '\n')
            tex_out.append(r'\caption{' + alt_text + r'}' + '\n')
            tex_out.append(r'\end{figure}' + '\n')
            continue

        # Headings
        if stripped.startswith('# '):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            title_text = re.sub(r'^#\s+', '', stripped)
            tex_out.append(r'\section{' + process_inline(title_text, is_log_file) + r'}' + '\n')
            continue
        elif stripped.startswith('## '):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            title_text = re.sub(r'^##\s+', '', stripped)
            tex_out.append(r'\subsection{' + process_inline(title_text, is_log_file) + r'}' + '\n')
            continue
        elif stripped.startswith('### '):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            title_text = re.sub(r'^###\s+', '', stripped)
            tex_out.append(r'\subsubsection{' + process_inline(title_text, is_log_file) + r'}' + '\n')
            continue
        elif stripped.startswith('#### '):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            title_text = re.sub(r'^####\s+', '', stripped)
            tex_out.append(r'\paragraph{' + process_inline(title_text, is_log_file) + r'}' + '\n')
            continue

        # Lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                tex_out.append(r'\begin{itemize}' + '\n')
                in_list = True
            item_text = stripped[2:]
            tex_out.append(r'\item ' + process_inline(item_text, is_log_file) + '\n')
            continue

        if not stripped:
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            tex_out.append('\n')
            continue

        # Horizontal Rule
        if stripped == '---':
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            tex_out.append(r'\hrule' + '\n\n')
            continue

        # Standalone Block Math ($$ ... $$)
        if not is_log_file and stripped.startswith('$$') and stripped.endswith('$$'):
            if in_list:
                tex_out.append(r'\end{itemize}' + '\n')
                in_list = False
            math_body = stripped[2:-2].strip()
            math_body = fix_math_subscripts(math_body)
            math_body = re.sub(r'(?<!\\)%', r'\%', math_body)
            tex_out.append(r'\[ ' + math_body + r' \]' + '\n\n')
            continue

        # Paragraph text
        tex_out.append(process_inline(stripped, is_log_file) + '\n\n')

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
        print(stdout_str[-1200:])

if __name__ == '__main__':
    md_path = 'reports/Assignment_Report.md'
    tex_path = 'reports/Assignment_Report.tex'
    md_to_tex(md_path, tex_path, is_log_file=False)
    compile_pdf(tex_path)

    llm_md = 'reports/LLM_Conversations.md'
    llm_tex = 'reports/LLM_Conversations.tex'
    if os.path.exists(llm_md):
        md_to_tex(llm_md, llm_tex, is_log_file=True)
        compile_pdf(llm_tex)
