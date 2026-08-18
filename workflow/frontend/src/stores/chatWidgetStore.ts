import { create } from 'zustand'

const STORAGE_KEY = 'biblioteca.chatWidget'

export type ChatWidgetSize = 'compact' | 'large'

export const CHAT_WIDGET_DEFAULTS: Record<ChatWidgetSize, { width: number; height: number }> = {
  compact: { width: 320, height: 480 },
  large: { width: 448, height: 640 },
}

interface PersistedChatWidgetState {
  size: ChatWidgetSize
  widthPx: number | null
  heightPx: number | null
}

interface ChatWidgetState extends PersistedChatWidgetState {
  toggleSize: () => void
  setSize: (size: ChatWidgetSize) => void
  setWidth: (width: number) => void
  setHeight: (height: number) => void
}

function loadPersisted(): PersistedChatWidgetState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { size: 'compact', widthPx: null, heightPx: null }
    const parsed = JSON.parse(raw) as Partial<PersistedChatWidgetState>
    return {
      size: parsed.size === 'large' ? 'large' : 'compact',
      widthPx: typeof parsed.widthPx === 'number' ? parsed.widthPx : null,
      heightPx: typeof parsed.heightPx === 'number' ? parsed.heightPx : null,
    }
  } catch {
    return { size: 'compact', widthPx: null, heightPx: null }
  }
}

function persist(state: PersistedChatWidgetState) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch {
    // almacenamiento no disponible: el tamaño se mantiene en memoria
  }
}

export const useChatWidgetStore = create<ChatWidgetState>((set, get) => ({
  ...loadPersisted(),
  toggleSize: () => {
    const nextSize: ChatWidgetSize = get().size === 'compact' ? 'large' : 'compact'
    const state: PersistedChatWidgetState = { size: nextSize, widthPx: null, heightPx: null }
    persist(state)
    set(state)
  },
  setSize: (size) => {
    const state: PersistedChatWidgetState = { size, widthPx: null, heightPx: null }
    persist(state)
    set(state)
  },
  setWidth: (width) => {
    const state: PersistedChatWidgetState = { ...get(), widthPx: width }
    persist(state)
    set(state)
  },
  setHeight: (height) => {
    const state: PersistedChatWidgetState = { ...get(), heightPx: height }
    persist(state)
    set(state)
  },
}))