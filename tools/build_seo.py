#!/usr/bin/env python3
"""Adds the Google (SEO) tags to index.html and builds ar/index.html from it.

Run after every change to index.html:  python3 tools/build_seo.py
index.html stays the only file to edit; ar/index.html is the same page that opens in Arabic,
so Google can index the Arabic version at its own address (shalabicpa.com/ar/).
"""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://shalabicpa.com'
NAME = 'משרד רואה חשבון שלבי עבדאלהאדי - המרכז להחזרי מס'
NAME_AR = 'مكتب المحاسب القانوني عبد الهادي شلبي - المركز لاسترجاع الضرائب'
SOCIAL = ['https://www.instagram.com/tax_center_iksal/', 'https://www.tiktok.com/@taxcenter.iksal',
          'https://www.facebook.com/share/1FJoxyZb8E/']

PAGES = {
    'he': dict(
        url=SITE + '/', locale='he_IL',
        title='החזר מס אכסאל ונצרת | רו״ח שלבי - המרכז להחזרי מס',
        desc='בדיקת זכאות להחזר מס חינם תוך דקה. משרד רואה חשבון עבדאלהאדי שלבי באכסאל: '
             'החזרי מס לשכירים ולפנסיונרים, משיכת כספים ודוחות שנתיים. 052-4310428',
        cities=['אכסאל', 'נצרת', 'נוף הגליל', 'יפיע', 'עין מאהל', 'דבוריה', 'כפר כנא', 'משהד', 'ריינה', 'עפולה'],
        area='שירות לתושבי {} והסביבה.', sep=', ',
    ),
    'ar': dict(
        url=SITE + '/ar/', locale='ar_IL',
        title='استرجاع ضريبة إكسال والناصرة | المحاسب شلبي - المركز لاسترجاع الضرائب',
        desc='افحصوا مجانًا خلال دقيقة إذا كان يحق لكم استرجاع ضريبة. مكتب المحاسب القانوني عبد الهادي شلبي في إكسال: '
             'استرجاع ضرائب للأجيرين والمتقاعدين، سحب أموال وتقارير سنوية. 052-4310428',
        cities=['إكسال', 'الناصرة', 'نوف هجليل', 'يافة الناصرة', 'عين ماهل', 'دبورية', 'كفر كنا', 'المشهد', 'الرينة', 'العفولة'],
        area='نخدم سكان {} والمنطقة.', sep='، ',
    ),
}


def head(lang):
    p = PAGES[lang]
    ld = {
        '@context': 'https://schema.org', '@type': 'AccountingService', '@id': SITE + '/#business',
        'name': NAME, 'alternateName': [NAME_AR, 'המרכז להחזרי מס ומשיכת כספים', 'المركز لاسترجاع الضرائب وسحب الأموال'],
        'description': p['desc'], 'url': p['url'], 'telephone': '+972-52-431-0428',
        'image': SITE + '/assets/og.png', 'logo': SITE + '/assets/logo.png',
        'address': {'@type': 'PostalAddress', 'streetAddress': 'Lara Center', 'addressLocality': 'Iksal',
                    'postalCode': '1692000', 'addressCountry': 'IL'},
        'openingHoursSpecification': [{'@type': 'OpeningHoursSpecification',
                                       'dayOfWeek': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday'],
                                       'opens': '09:00', 'closes': '15:00'}],
        'areaServed': [{'@type': 'City', 'name': c} for c in p['cities']],
        'founder': {'@type': 'Person', 'name': 'עבדאלהאדי שלבי', 'alternateName': 'عبد الهادي شلبي',
                    'jobTitle': 'Certified Public Accountant'},
        'knowsLanguage': ['he', 'ar'], 'sameAs': SOCIAL,
    }
    e = lambda s: s.replace('&', '&amp;').replace('"', '&quot;')
    return '\n'.join([
        '<!-- seo:start (נוצר על ידי tools/build_seo.py) -->',
        f'<title>{p["title"]}</title>',
        f'<meta name="description" content="{e(p["desc"])}">',
        f'<link rel="canonical" href="{p["url"]}">',
        f'<link rel="alternate" hreflang="he" href="{PAGES["he"]["url"]}">',
        f'<link rel="alternate" hreflang="ar" href="{PAGES["ar"]["url"]}">',
        f'<link rel="alternate" hreflang="x-default" href="{PAGES["he"]["url"]}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta property="og:type" content="website">',
        f'<meta property="og:url" content="{p["url"]}">',
        f'<meta property="og:title" content="{e(p["title"])}">',
        f'<meta property="og:description" content="{e(p["desc"])}">',
        f'<meta property="og:image" content="{SITE}/assets/og.png">',
        f'<meta property="og:locale" content="{p["locale"]}">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<link rel="icon" type="image/png" href="/assets/logo.png">',
        '<link rel="apple-touch-icon" href="/assets/logo.png">',
        '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script>',
        '<!-- seo:end -->',
    ])


def area_line(lang):
    p = PAGES[lang]
    return f'<span class="disclaimer area">{p["area"].format(p["sep"].join(p["cities"]))}</span>'


def sub(pattern, repl, s, count=1):
    out, n = re.subn(pattern, lambda m: repl, s, count=count, flags=re.S)
    if n != count:
        raise SystemExit(f'pattern not found {count}x: {pattern}')
    return out


src_path = ROOT / 'index.html'
src = src_path.read_text(encoding='utf-8')

# Head: replace the old <title> (first run) or the previous seo block.
if '<!-- seo:start' in src:
    src = sub(r'<!-- seo:start.*?<!-- seo:end -->', head('he'), src)
else:
    src = sub(r'<title>[^<]*</title>', head('he'), src)

# Service-area line at the bottom of each language's footer.
src = re.sub(r'\n    <span class="disclaimer area">[^<]*</span>', '', src)
for lang, marker in (('he', 'ואינו גוף ממשלתי.</span>'), ('ar', 'وليس جهة حكومية.</span>')):
    src = sub(re.escape(marker), marker + '\n    ' + area_line(lang), src)

src_path.write_text(src, encoding='utf-8')

# Arabic page: same file, Arabic shown first and as the page language.
ar = sub(r'<!-- seo:start.*?<!-- seo:end -->', head('ar'), src)
ar = sub(r'<html lang="he"', '<html lang="ar"', ar)
ar = sub(r'<div data-lang="he" lang="he">', '<div data-lang="he" lang="he" hidden>', ar)
ar = sub(r'<div data-lang="ar" lang="ar" hidden>', '<div data-lang="ar" lang="ar">', ar)
ar = sub(re.escape('<a class="lang-sw" href="#he" lang="he">'), '<a class="lang-sw" href="/" lang="he">', ar)
ar = sub(re.escape("lang=(h==='#ar'||/-ar$/.test(h))?'ar':'he'"), "lang=(!h||h==='#ar'||/-ar$/.test(h))?'ar':'he'", ar)
(ROOT / 'ar').mkdir(exist_ok=True)
(ROOT / 'ar' / 'index.html').write_text(ar, encoding='utf-8')
print('ok: index.html, ar/index.html')
