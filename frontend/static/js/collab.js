import * as Y from 'yjs'
import { yCollab } from 'y-codemirror.next'
import { WebsocketProvider } from 'y-websocket';

export const userColors = [
    { color: '#30bced', light: '#30bced33' },
    { color: '#6eeb83', light: '#6eeb8333' },
    { color: '#ffbc42', light: '#ffbc4233' },
    { color: '#ecd444', light: '#ecd44433' },
    { color: '#ee6352', light: '#ee635233' },
    { color: '#9ac2c9', light: '#9ac2c933' },
    { color: '#8acb88', light: '#8acb8833' },
    { color: '#1be7ff', light: '#1be7ff33' }
]

const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://'
const wsHost = window.location.hostname
const wsPort = 1234
const wsUrl = wsProtocol + wsHost + ':' + wsPort

class CollaborationManager {
    constructor () {
        this.editor = null
        this.isActive = false
        this.ydoc = null
        this.provider = null
        this.ytext = null
        this.collabCompartment = null
    }

    setCompartment (compartment) {
        this.collabCompartment = compartment
    }

    connect (roomId, userName, editorInstance) {
        if (!this.isActive && this.collabCompartment) {
            this.editor = editorInstance
            this.isActive = true
            this.ydoc = new Y.Doc()
            this.provider = new WebsocketProvider(wsUrl, roomId, this.ydoc)
            this.ytext = this.ydoc.getText('codemirror')

            let color = userColors[Math.floor((Math.random() * userColors.length))]

            this.provider.awareness.setLocalStateField('user', {
                name: userName,
                color: color.color,
                colorLight: color.light
            })

            const undoManager = new Y.UndoManager(this.ytext)

            const collabExtension = yCollab(this.ytext, this.provider.awareness, { undoManager })
            this.editor.dispatch({
                effects: this.collabCompartment.reconfigure(collabExtension),
            })

        }
    }

    disconnect () {
        if (this.isActive) {
            if (this.editor && this.collabCompartment) {
                this.editor.dispatch({
                    effects: this.collabCompartment.reconfigure([])
                })
            }
            this.ydoc.destroy()
            this.provider.disconnect()
            this.ytext = null
            this.editor = null
            this.isActive = false
        }
    }

    getContent () {
        return this.ytext ? this.ytext.toString() : ""
    }

}

export const collabManager = new CollaborationManager()
