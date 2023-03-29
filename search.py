import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import threading
import platform
import traceback

num_files = 0  # 总文件数
stop = False


def open_file(filepath):
    if platform.system() == 'Windows':
        os.startfile(filepath)
    else:
        opener = "open" if platform.system() == "Darwin" else "xdg-open"
        os.system(f'{opener} "{filepath}"')


def on_double_click(result_text, event):
    # 获取双击位置的索引
    index = result_text.index("@%d,%d" % (event.x, event.y))
    # 提取出行号，并输出到控制台
    line_num = int(index.split('.')[0])
    return line_num


def prepare_progressbar(path):
    num_files = 0
    for dirpath, dirs, files in os.walk(path):
        num_files += len(files)
    progress_var.configure(maximum=num_files, value=0)


def update_progressbar():
    progress_var.step(1)
    if progress_var['value'] == num_files:
        progress_var.stop()


def search_files(keywords, path, suffix, encoding):
    results = []
    global stop

    for dirpath, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(suffix):
                filepath = os.path.join(dirpath, file)
                with open(filepath, "r", errors='ignore', encoding=encoding) as f:
                    content = f.read()
                    if all(keyword in content for keyword in keywords):
                        results.append(filepath)
                        # 将搜索到的文件路径插入到结果文本框中，并为其添加事件绑定
                        result_text.insert(tk.END, f"{filepath}\n", "clickable")
                        result_text.tag_bind("clickable", "<Double-Button-1>",
                                             lambda e: open_file(results[on_double_click(result_text, e) - 1]))
            if stop:
                break
            update_progressbar()
    return results, num_files


def start_search():
    global search_thread
    global stop
    folder_path = folder_entry.get()
    prepare_progressbar(folder_path)
    if folder_path:
        keywords = keyword_entry.get().split()
        suffix = suffix_combobox.get()
        encoding = encoding_combobox.get()

        # 在开始搜索时，清空结果文本框中的内容和事件绑定
        result_text.delete("1.0", tk.END)
        result_text.tag_delete("clickable")

        stop = False
        global search_thread
        search_thread = threading.Thread(target=search_files,
                                         args=(keywords, folder_path, suffix, encoding))
        search_thread.start()


def browse_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder_path)


def stop_search():
    global stop
    if search_thread and search_thread.is_alive():
        stop = True


root = tk.Tk()
root.title("File Search Tool")

# 关键字输入框和文件夹浏览按钮
keyword_label = tk.Label(root, text="Enter keywords (separated by spaces):")
keyword_label.pack()
keyword_entry = tk.Entry(root)
keyword_entry.pack()

folder_frame = tk.Frame(root)
folder_frame.pack(fill=tk.X, pady=10)

folder_entry = tk.Entry(folder_frame)
folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

folder_browse_button = tk.Button(folder_frame, text="Browse", command=browse_folder)
folder_browse_button.pack(side=tk.LEFT)

# 后缀选择下拉菜单
suffix_label = tk.Label(root, text="File suffix:")
suffix_label.pack()

suffix_combobox = ttk.Combobox(root, values=[".md", ".txt", ".docx", ".pdf"])
suffix_combobox.current(0)
suffix_combobox.pack()

# 打开文件编码选择下拉菜单
encoding_label = tk.Label(root, text="Open file encoding:")
encoding_label.pack()

encoding_combobox = ttk.Combobox(root, values=["utf-8", "gbk", "gb2312"])
encoding_combobox.current(0)
encoding_combobox.pack()

# 开始搜索按钮和进度条
search_button = tk.Button(root, text="Start Search", command=start_search)
search_button.pack(side=tk.TOP)
# 停止搜索
stop_button = tk.Button(root, text="Stop Search", command=stop_search)
stop_button.pack(side=tk.TOP)

progress_var = ttk.Progressbar(root, orient=tk.HORIZONTAL, mode='determinate')
progress_var.pack(fill=tk.X, padx=10, pady=10)

# 搜索结果文本框和文件数量显示
result_label = tk.Label(root, text="Search Results:")
result_label.pack()

y_scrollbar = tk.Scrollbar(root)

result_text = tk.Text(root)
result_text.config(yscrollcommand=y_scrollbar.set)
y_scrollbar.config(command=result_text.yview)

result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

root.mainloop()
