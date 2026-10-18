import { useTheme } from '../theme'

export function useEditorTheme() {
  const { resolvedTheme } = useTheme()
  return resolvedTheme === 'dark' ? 'vs-dark' : 'light'
}
