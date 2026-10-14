/**
 * תיבת קליטה לפניות מהאתר (Google Apps Script, צמוד לגיליון Google פרטי של המשרד).
 *
 * האתר שולח לכאן כל פנייה (שאלון, "חזרו אליי", צור קשר) והיא נרשמת בלשונית "leads".
 * AMS לא חשוף לאינטרנט, ולכן הוא זה שפונה לכאן: מושך פניות חדשות (pending) עם מפתח,
 * ואחרי שקלט כל אחת מסמן אותה (ack). קבצים מצורפים לא עוברים כאן בכלל.
 *
 * הגדרה חד-פעמית: Project Settings → Script properties → AMS_KEY = מפתח סודי ארוך,
 * אותו ערך שמוגדר ב-AMS (WEB_LEADS_KEY).
 */
/* להרצה פעם אחת מהעורך (Run → setupKey): יוצר מפתח אקראי ומציג אותו ביומן. */
function setupKey() {
  var p = PropertiesService.getScriptProperties();
  if (!p.getProperty('AMS_KEY')) p.setProperty('AMS_KEY', (Utilities.getUuid() + Utilities.getUuid()).replace(/-/g, ''));
  sheet_();
  Logger.log('AMS_KEY = ' + p.getProperty('AMS_KEY'));
}

var SHEET = 'leads';
var HEAD = ['lead_id', 'received_at', 'form', 'lang', 'name', 'phone', 'email', 'message', 'answers', 'status', 'ams_customer_id', 'done_at'];

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET) || ss.insertSheet(SHEET);
  if (sh.getLastRow() === 0) sh.appendRow(HEAD);
  return sh;
}

function out_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

function clip_(v, n) {
  return String(v == null ? '' : v).replace(/[\u0000-\u001f]/g, ' ').trim().slice(0, n);
}

/* קליטה מהאתר. הגוף נשלח כ-text/plain כדי שהדפדפן לא יבצע preflight. */
function doPost(e) {
  try {
    var b = JSON.parse(e.postData.contents);
    if (b.website) return out_({ ok: true });          // מלכודת בוטים: שדה מוסתר שאדם לא ממלא
    var name = clip_(b.name, 120);
    var phone = clip_(b.phone, 30).replace(/[^\d+]/g, '');
    if (!name || phone.replace(/\D/g, '').length < 9) return out_({ ok: false, error: 'missing' });
    var answers = b.answers && typeof b.answers === 'object' ? b.answers : {};

    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      sheet_().appendRow([Utilities.getUuid(), new Date(), clip_(b.form, 20), clip_(b.lang, 5), name, "'" + phone,  // ' כדי ש-Sheets לא יהפוך למספר ויוריד את ה-0
        clip_(b.email, 120), clip_(b.message, 3000), JSON.stringify(answers).slice(0, 3000), 'new', '', '']);
    } finally {
      lock.releaseLock();
    }
    return out_({ ok: true });
  } catch (err) {
    return out_({ ok: false, error: 'server' });
  }
}

/* פנייה מ-AMS. כל הפעולות דורשות key=AMS_KEY.
 *   ?action=pending                          → עד 50 פניות בסטטוס new
 *   ?action=ack&lead_id=..&customer_id=..    → מסמן שהפנייה נקלטה ב-AMS */
function doGet(e) {
  var key = PropertiesService.getScriptProperties().getProperty('AMS_KEY');
  var p = e.parameter || {};
  if (!key || !p.key || p.key !== key) return out_({ ok: false, error: 'auth' });

  var sh = sheet_(), rows = sh.getDataRange().getValues(), col = {};
  HEAD.forEach(function (h, i) { col[h] = i; });

  if (p.action === 'pending') {
    var list = [];
    for (var r = 1; r < rows.length && list.length < 50; r++) {
      if (rows[r][col.status] !== 'new') continue;
      var o = {};
      HEAD.forEach(function (h) { o[h] = rows[r][col[h]]; });
      o.received_at = Utilities.formatDate(new Date(o.received_at), 'Asia/Jerusalem', 'yyyy-MM-dd HH:mm:ss');
      o.phone = String(o.phone);
      list.push(o);
    }
    return out_({ ok: true, leads: list });
  }

  if (p.action === 'ack') {
    for (var i = 1; i < rows.length; i++) {
      if (rows[i][col.lead_id] !== p.lead_id) continue;
      sh.getRange(i + 1, col.status + 1).setValue('done');
      sh.getRange(i + 1, col.ams_customer_id + 1).setValue(String(p.customer_id || ''));
      sh.getRange(i + 1, col.done_at + 1).setValue(new Date());
      return out_({ ok: true });
    }
    return out_({ ok: false, error: 'not_found' });
  }
  return out_({ ok: false, error: 'action' });
}
