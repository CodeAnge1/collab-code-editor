const maxLength = 500000;

var editorInstance;
var currentFileName = 'untitled.txt';
var currentTheme = 'dracula';

const themes = [
    "3024-day", "3024-night", "abbott", "abcdef", "ambiance-mobile", "ambiance",
    "ayu-dark", "ayu-mirage", "base16-dark", "base16-light", "bespin", "blackboard",
    "cobalt", "colorforth", "darcula", "dracula", "duotone-dark", "duotone-light",
    "eclipse", "elegant", "erlang-dark", "gruvbox-dark", "hopscotch", "icecoder", "idea",
    "isotope", "juejin", "lesser-dark", "liquibyte", "lucario", "material-darker",
    "material-ocean", "material-palenight", "material", "mbo", "mdn-like", "midnight",
    "monokai", "moxer", "neat", "neo", "night", "nord", "oceanic-next", "panda-syntax",
    "paraiso-dark", "paraiso-light", "pastel-on-dark", "railscasts", "rubyblue", "seti",
    "shadowfox", "solarized", "ssms", "the-matrix", "tomorrow-night-bright",
    "tomorrow-night-eighties", "ttcn", "twilight", "vibrant-ink", "xq-dark", "xq-light",
    "yeti", "yonce", "zenburn"
];

document.addEventListener('DOMContentLoaded', function () {
    initEditor();

    document.querySelector('.settings-btn').addEventListener('click', showSettings)
    document.querySelector('.close').addEventListener('click', closeSettings)
    document.querySelector('.save-btn').addEventListener('click', saveSettings)

    const filenameInput = document.getElementById('file-name-input')

    filenameInput.addEventListener('input', function (e) {
        updateFileName(e.target.value)
    })

    filenameInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter') {
            loadModeByFileName(filenameInput.value.trim())
        }
    })

    const searchInput = document.getElementById('theme-search-input')
    const dropdown = document.getElementById('theme-list')
    let highlightedIndex = -1;
    let lastPressedKey = null;

    searchInput.addEventListener('focus', () => {
        dropdown.classList.add('show')
        searchInput.value = ''
        renderThemeList()
        highlightedIndex = themes.indexOf(currentTheme)
        highlightItem(dropdown.querySelectorAll('.theme-item'), highlightedIndex)
    })

    searchInput.addEventListener('blur', () => {
        setTimeout(() => {
            if (!dropdown.contains(document.activeElement)) {
                dropdown.classList.remove('show')
            }
        }, 250)
    })

    searchInput.addEventListener('input', () => {
        renderThemeList()
        highlightedIndex = 0
        highlightItem(dropdown.querySelectorAll('.theme-item'), 0)
    })

    searchInput.addEventListener('keydown', (e) => {
        const items = dropdown.querySelectorAll('.theme-item')
        if (e.key === 'ArrowDown') {
            highlightedIndex = (highlightedIndex + 1) % items.length
            highlightItem(items, highlightedIndex)
        } else if (e.key === 'ArrowUp') {
            highlightedIndex = highlightedIndex <= 0 ? items.length - 1 : highlightedIndex - 1
            highlightItem(items, highlightedIndex)
        } else if (e.key === 'Enter') {
            const indexToSelect = highlightedIndex >= 0 ? highlightedIndex : 0
            const theme = items[indexToSelect].dataset.theme
            applyTheme(theme)
            searchInput.value = theme
            if (lastPressedKey === 'Enter') {
                dropdown.classList.remove('show')
                searchInput.blur()
                highlightedIndex = 0
            }
        } else if (e.key === 'Escape') {
            dropdown.classList.remove('show')
            searchInput.blur()
            highlightedIndex = 0
        }
        lastPressedKey = e.key
    })

    dropdown.addEventListener('click', (e) => {
        const item = e.target.closest('.theme-item')
        if (item) {
            applyTheme(item.dataset.theme)
            searchInput.value = item.dataset.theme
            dropdown.classList.remove('show')
            searchInput.blur()
        }
    })

    document.addEventListener('click', (e) => {
        const inInput = searchInput.contains(e.target)
        const inDropdown = dropdown.contains(e.target)

        if (!inInput && !inDropdown) {
            dropdown.classList.remove('show')
        }
        if (e.target === document.getElementById('settings-popup')) {
            closeSettings()
        }
    })
})

function initEditor() {
    const codeTextarea = document.getElementById("code-input")
    editorInstance = CodeMirror.fromTextArea(codeTextarea, {
        lineNumbers: true,
        theme: "dracula",
        styleActiveLine: true,
        scrollbarStyle: "overlay",
        mode: "text/plain",
        indentUnit: 4,
    })

    const style = document.createElement('style')
    style.textContent = '.CodeMirror { height: 100% !important; }'
    document.head.appendChild(style)

    editorInstance.on('change', function () {
        const value = editorInstance.getValue()
        if (value.length > maxLength) {
            const cursor = editorInstance.getCursor()
            editorInstance.setValue(value.slice(0, maxLength));
            editorInstance.setCursor(cursor)
            alert('Character limit exceeded:' + maxLength);
        }
    })
}

function highlightItem(items, index) {
    items.forEach((item, i) => {
        item.classList.toggle('highlighted', i === index)
    })
    items[index]?.scrollIntoView({block: 'nearest', behavior: 'smooth'})
}

function renderThemeList() {
    const input = document.getElementById('theme-search-input')
    const list = document.getElementById('theme-list')
    const term = input.value.toLowerCase()

    list.innerHTML = ''

    themes
        .filter(t => t.toLowerCase().includes(term))
        .forEach(theme => {
            const item = document.createElement('div')
            item.className = 'theme-item'
            if (theme === currentTheme) {
                item.classList.add('active')
            }
            item.dataset.theme = theme
            item.textContent = theme
            list.appendChild(item)
        })
}

function applyTheme(themeName) {
    currentTheme = themeName

    document.querySelectorAll('link[data-codemirror-theme]').forEach(l => l.remove())

    if (currentTheme) {
        const link = document.createElement('link')
        link.rel = 'stylesheet'
        link.href = `../lib/codemirror/theme/${currentTheme}.css`
        link.setAttribute('data-codemirror-theme', '')
        link.onload = () => editorInstance.setOption('theme', currentTheme)
        document.head.appendChild(link)
    } else {
        editorInstance.setOption('theme', '')
    }
}

function updateFileName(name) {
    currentFileName = name || 'untitled.txt'
    document.querySelector('#current-file-tab .file-tab-name').textContent = currentFileName
}

function showSettings() {
    const popup = document.getElementById('settings-popup')
    popup.classList.add('active')
    document.getElementById('file-name-input').value = currentFileName
    document.getElementById('theme-search-input').value = currentTheme === '' ? '' : currentTheme
    document.getElementById('file-name-input').focus()
}

function closeSettings() {
    document.getElementById('settings-popup').classList.remove('active')
}

function saveSettings() {
    const newName = document.getElementById('file-name-input').value.trim() || 'untitled.txt'
    updateFileName(newName)
    loadModeByFileName(newName)
    closeSettings()
}

function loadModeByFileName(filename) {
    let info = CodeMirror.findModeByFileName(filename)
    info = info ? info : CodeMirror.findModeByFileName(filename + ".txt")

    if (!CodeMirror.modes[info.mode]) {
        const script = document.createElement('script')
        script.src = `../lib/codemirror/mode/${info.mode}/${info.mode}.js`
        script.onload = () => editorInstance.setOption('mode', info.mime)
        document.head.appendChild(script)
    } else {
        editorInstance.setOption('mode', info.mime)
    }
}