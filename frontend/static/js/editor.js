import { EditorView, lineNumbers, highlightActiveLine } from "@codemirror/view";
import { indentMore, indentLess } from '@codemirror/commands';
import { Compartment, EditorState } from "@codemirror/state";
import { languages } from '@codemirror/language-data';
import {indentUnit} from "@codemirror/language";
import { minimalSetup } from "codemirror";
import {
    abcdef, abyss, androidstudio, andromeda,
    atomone, aura, bespin, dracula,
    gruvboxDark, kimbie, material, monokai,
    monokaiDimmed, noctisLilac, nord, okaidia,
    quietlight, red, tokyoNight, tokyoNightStorm,
    tokyoNightDay, tomorrowNightBlue
} from '@uiw/codemirror-themes-all';

import { collabManager } from './collab.js'


const maxLength = 500000;
let currentFileName = 'untitled.txt';
let currentTheme = 'dracula';

let editorInstance;
const themeConfig = new Compartment();
const languageConfig = new Compartment();
const collabConfig = new Compartment()

const themeMap = {
    "abcdef": abcdef,
    "abyss": abyss,
    "androidstudio": androidstudio,
    "andromeda": andromeda,
    "atomone": atomone,
    "aura": aura,
    "bespin": bespin,
    "dracula": dracula,
    "gruvbox-dark": gruvboxDark,
    "kimbie": kimbie,
    "material": material,
    "monokai": monokai,
    "monokai-dimmed": monokaiDimmed,
    "noctis-lilac": noctisLilac,
    "nord": nord,
    "okaidia": okaidia,
    "quietlight": quietlight,
    "red": red,
    "tokyo-night": tokyoNight,
    "tokyo-night-storm": tokyoNightStorm,
    "tokyo-night-day": tokyoNightDay,
    "tomorrow-night-blue": tomorrowNightBlue
};

const themes = Object.keys(themeMap);

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

function checkMaxLength(update) {
    const curLength = update.state.doc.length;
    if (curLength > maxLength) {
        const cursor = update.state.selection.main;
        cursor.from = cursor.from > maxLength ? maxLength : cursor.from;
        cursor.to = cursor.to > maxLength ? maxLength : cursor.to;
        update.view.dispatch({
            changes: {
                from: maxLength,
                to: curLength,
                insert: ''
            },
            selection: cursor
        });
        alert('Character limit exceeded: ' + maxLength);
    }
}

const maxLengthExtension = EditorView.updateListener.of((update) => {
    if (update.docChanged) checkMaxLength(update);
})

function initEditor() {
    let state = EditorState.create({
        extensions: [
            minimalSetup,
            themeConfig.of(themeMap[currentTheme]),
            languageConfig.of([]),
            lineNumbers(),
            highlightActiveLine(),
            EditorState.tabSize.of(4),
            indentUnit.of("    "),
            EditorView.domEventHandlers({
                keydown: (event, view) => {
                    if (event.key === "Tab") {
                        event.preventDefault();
                        if (event.shiftKey) {
                            indentLess(view);
                        } else {
                            indentMore(view);
                        }
                        return true;
                    }
                    return false;
                }
            }),
            maxLengthExtension,
            collabConfig.of([]),
        ],
    });
    editorInstance = new EditorView({
        state,
        parent: document.querySelector("#code-editor"),
    });
    const style = document.createElement('style')
    style.textContent = '.cm-editor { height: 100% !important; }'
    document.head.appendChild(style)

    collabManager.setCompartment(collabConfig);
    setTimeout(() => {
        const roomId = window.location.pathname.split('/').pop()
        const userName = 'User_' + Math.floor(Math.random() * 10)
        collabManager.connect(roomId, userName, editorInstance);
    }, 500)
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
    const theme = themeMap[themeName];

    currentTheme = themeName;

    editorInstance.dispatch({
        effects: themeConfig.reconfigure(theme)
    });

    document.querySelectorAll('.theme-item').forEach(item => {
        item.classList.toggle('active', item.dataset.theme === themeName);
    });
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

function setLanguage(language) {
    editorInstance.dispatch({
        effects: languageConfig.reconfigure(language || [])
    });
}

async function loadLanguage(languageDescription) {
    try {
        const language = await languageDescription.load();
        setLanguage(language);
    } catch (error) {
        setLanguage(null);
    }
}

function loadModeByFileName(filename) {
    const languageDesc = languages.find(lang =>
            lang.extensions && lang.extensions.some(ext =>
                filename.toLowerCase().endsWith(ext.toLowerCase())
            )
    );
    if (languageDesc) {
        loadLanguage(languageDesc);
    } else {
        setLanguage(null);
    }
}