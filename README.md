# אתר המשרד

האתר כולו נמצא בקובץ אחד: `index.html` (עברית וערבית, `#ar` לערבית).
הטפסים שולחים מייל ל־Taxcenter9@gmail.com דרך FormSubmit; בפעם הראשונה מגיע מייל אישור שצריך ללחוץ עליו.

## גוגל (SEO)
אחרי כל שינוי ב־`index.html` מריצים `python3 tools/build_seo.py`. הסקריפט מעדכן את הכותרת, התיאור ופרטי העסק לגוגל, ובונה את `ar/index.html` (אותו דף שנפתח בערבית, בכתובת shalabicpa.com/ar/). את `ar/index.html` לא עורכים ידנית.
`sitemap.xml` ו־`robots.txt` נמצאים בשורש האתר.
