import en from './en.json';
import zh from './zh.json';

const translations: Record<string, Record<string, string>> = { en, zh };

export function getLangFromUrl(url: URL): string {
  const [, lang] = url.pathname.split('/');
  if (lang === 'zh') return 'zh';
  return 'en';
}

export function t(lang: string, key: string): string {
  return translations[lang]?.[key] ?? translations.en[key] ?? key;
}

export function localePath(lang: string, path: string): string {
  let clean = path.replace(/^\/?(en|zh)\//, '/');
  clean = clean.replace(/\/+$/, '') || '/';
  if (lang === 'en') return clean === '/' ? '/' : `${clean}/`;
  if (clean === '/') return '/zh/';
  return `/zh${clean}/`;
}

export function altLang(lang: string): string {
  return lang === 'en' ? 'zh' : 'en';
}

export function htmlLang(lang: string): string {
  return lang === 'zh' ? 'zh-Hans' : 'en';
}
