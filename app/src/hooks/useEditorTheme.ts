import { useEffect, useState } from 'react'

export function useEditorTheme() {
  const [editorTheme, setEditorTheme] = useState<'light' | 'vs-dark'>('light')

  useEffect(() => {
    const updateTheme = () => {
      setEditorTheme(document.documentElement.classList.contains('dark') ? 'vs-dark' : 'light')
    }

    updateTheme()
    const observer = new MutationObserver(updateTheme)
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })
    return () => observer.disconnect()
  }, [])

  return editorTheme
}