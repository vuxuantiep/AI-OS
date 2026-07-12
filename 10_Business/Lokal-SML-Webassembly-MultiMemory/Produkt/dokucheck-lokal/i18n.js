/* DokuCheck Lokal — Mehrsprachigkeit (Deutsch / English / Tiếng Việt).
   Locker und leicht verständlich formuliert. Die gewählte Sprache steuert
   auch die Antwortsprache des KI-Modells (siehe prompt.*-Schlüssel).
   Gemerkt wird die Wahl im session-Store (Tool Memory). */
import { sessionGet, sessionSet } from "./memory/db.js";

const UEBERSETZUNGEN = {
  /* ================= DEUTSCH ================= */
  de: {
    "html.title": "DokuCheck Lokal — KI-Dokumentanalyse ohne Cloud",
    "proof.mode": "LOKALER MODUS",
    "proof.model": "Modell-Download (einmalig):",
    "proof.requests": "Anfragen",
    "proof.analysis": "Externe Anfragen bei Analyse:",
    "proof.ok": "Deine Dokumente verlassen dieses Gerät nicht.",
    "proof.alert": "Achtung: externe Netzwerkaktivität erkannt!",

    "hero.eyebrow": "Souveräne KI · Läuft in deinem Browser",
    "hero.lede": "Lade einen Vertrag, Behördenbrief oder ein Foto eines Dokuments hoch. Eine kleine KI liest, analysiert und übersetzt alles direkt auf deinem Gerät — ohne Server, ohne Cloud-Konto. Prüf es selbst: Öffne die Entwicklertools (F12 → Netzwerk) während der Analyse.",

    "gpu.title": "WebGPU nicht verfügbar",
    "gpu.intro": "Die KI-Analyse braucht WebGPU. So bekommst du es:",
    "gpu.desktop": "Desktop: Chrome oder Edge ab Version 113 verwenden; Status unter chrome://gpu bzw. edge://gpu prüfen.",
    "gpu.android": "Android: Chrome ab Version 121 (Android 12+).",
    "gpu.ios": "iPhone/iPad: Safari ab iOS 18 mit aktiviertem WebGPU.",
    "gpu.ocrNote": "Texterkennung (OCR) aus Fotos funktioniert trotzdem — sie läuft auf jedem Gerät.",
    "gpu.okBadge": "WebGPU verfügbar ✓",
    "gpu.missingBadge": "Kein WebGPU — Analyse deaktiviert, OCR funktioniert.",

    "s1.tag": "Schritt 1",
    "s1.title": "KI-Modell auf dein Gerät laden",
    "s1.modelLabel": "Modell:",
    "s1.m1": "Llama 3.2 1B — leicht, auch für Smartphones (~0,8 GB)",
    "s1.m2": "Qwen3 1.7B — schnell, gutes Deutsch (~1,2 GB)",
    "s1.m3": "Llama 3.2 3B — ausgewogen, braucht mehr Speicher (~2 GB)",
    "s1.loadBtn": "Modell laden",
    "s1.switchBtn": "Modell wechseln",
    "s1.hint": "Einmaliger Download — wird im Browser gespeichert. Danach klappt die Analyse auch offline.",
    "s1.cached": "Dieses Modell ist schon auf dem Gerät — Laden geht ohne Download.",
    "s1.ready": "Modell bereit — ab jetzt zählt der Netzwerk-Beweis.",
    "s1.error": "Fehler beim Laden:",

    "s2.tag": "Schritt 2",
    "s2.title": "Dokument auswählen",
    "drop.title": "PDF, Textdatei oder Foto hierher ziehen",
    "drop.or": "oder tippen zum Auswählen.",
    "drop.note": "Alles passiert lokal — die Datei wird nirgendwohin gesendet.",
    "camera.btn": "📷 Foto aufnehmen (OCR)",
    "ocr.l1": "OCR: Deutsch + Englisch",
    "ocr.l2": "OCR: nur Deutsch",
    "ocr.l3": "OCR: Vietnamesisch",
    "ocr.l4": "OCR: Deutsch + Englisch + Vietnamesisch",
    "ocr.running": "Texterkennung läuft …",
    "ocr.done": "Texterkennung fertig (lokal auf deinem Gerät).",
    "ocr.none": "Kein Text erkannt — versuch ein schärferes, gerades Foto.",
    "ocr.error": "OCR-Fehler:",
    "file.reading": "Lese:",
    "file.error": "Fehler beim Lesen:",
    "file.chars": "Zeichen",
    "file.sections": "Abschnitte (lokal verarbeitet)",
    "file.fromMemory": "aus dem Gedächtnis geladen",

    "s3.tag": "Schritt 3",
    "s3.title": "Analysieren & Übersetzen",
    "btn.sum": "Zusammenfassen",
    "btn.risk": "Worauf muss ich achten?",
    "btn.trans": "Übersetzen",
    "btn.stop": "Stopp",
    "btn.ask": "Fragen",
    "lang.de": "Deutsch",
    "lang.en": "Englisch",
    "lang.vi": "Vietnamesisch",
    "out.placeholder": "Die Analyse erscheint hier, sobald Modell und Dokument bereit sind.",
    "qa.placeholder": "Eigene Frage zum Dokument stellen …",
    "disclaimer": "Hinweis: DokuCheck Lokal gibt dir eine erste Einschätzung durch eine kleine KI — das ist keine Rechtsberatung. Bei wichtigen Verträgen und Fristen frag bitte eine Anwältin, einen Anwalt oder eine Beratungsstelle. Kleine Modelle können Fehler machen — prüfe wichtige Aussagen immer im Originaltext.",
    "err.prefix": "Fehler:",

    "mem.tag": "🧠 Gedächtnis",
    "mem.title": "Was sich DokuCheck merkt — lokal in deinem Browser",
    "mem.analysen": "Analyse-Verlauf",
    "mem.dokumente": "Gespeicherte Dokumente",
    "mem.routinen": "Prüfroutinen",
    "mem.emptyAnalysen": "Noch keine Analysen.",
    "mem.emptyDokumente": "Noch keine Dokumente.",
    "mem.emptyRoutinen": "Noch keine Routinen.",
    "mem.show": "Anzeigen",
    "mem.open": "Öffnen",
    "mem.run": "Ausführen",
    "mem.edit": "Bearbeiten",
    "mem.delete": "Löschen",
    "mem.save": "Speichern",
    "mem.export": "Export",
    "mem.import": "Import",
    "mem.namePh": "Name, z. B. „Miet-Check“",
    "mem.promptPh": "Anweisung, z. B. „Prüfe Kündigungsfristen und Nebenkosten …“",
    "mem.note": "Working Memory = aktuelles Dokument & Sitzung · Tool Memory = gemerkte Modell- und Sprachwahl. Alles liegt in der IndexedDB deines Browsers — nichts davon verlässt dein Gerät.",
    "mem.imported": "Routine(n) importiert.",
    "mem.importFailed": "Import fehlgeschlagen:",

    "action.sum": "Zusammenfassung",
    "action.risk": "Risiko-Check",
    "action.q": "Frage",
    "action.trans": "Übersetzung",
    "action.routine": "Routine:",
    "status.sumPart": "Fasse Teil {i}/{n} zusammen …",
    "note.sumLong": "(Hinweis: Das Dokument ist sehr lang — die ersten {max} von {n} Teilen wurden berücksichtigt.)",
    "note.transLong": "(Hinweis: Sehr langes Dokument — die ersten {max} von {n} Abschnitten wurden übersetzt.)",

    "step.ready": "✓ bereit",
    "hint.needModel": "Dokument ist bereit ✓ — lade jetzt noch das KI-Modell in Schritt 1, dann kann es losgehen.",
    "hint.goStep3": "Alles bereit ✓ — weiter mit Schritt 3: Analysieren & Übersetzen.",
    "pdf.scanned": "Gescanntes PDF erkannt (keine Textebene) — Texterkennung läuft …",
    "pdf.ocrPage": "Seite {i}/{n} …",
    "pdf.noText": "Kein Text erkennbar. Prüfe die OCR-Sprache oder versuch ein schärferes Foto/PDF.",
    "pdf.limited": "(Hinweis: Nur die ersten {n} Seiten wurden per OCR gelesen.)",

    "footer": "DokuCheck Lokal v0.2 · Technik: WebLLM 0.2.79 (MLC AI, Apache 2.0) + WebGPU · Tesseract.js 5.1.1 (OCR) + pdf.js 4.4.168 — alle Bibliotheken lokal gebündelt, keine CDN-Zugriffe. Teil der Edge Cognitive AI Platform.",

    "prompt.sys": "Du bist ein sorgfältiger Assistent, der Dokumente für Laien verständlich erklärt. Antworte auf Deutsch, locker, klar und knapp. Erfinde nichts: Wenn eine Information nicht im Text steht, sage das ausdrücklich.",
    "prompt.sumShort": "Fasse das folgende Dokument in einfachem Deutsch zusammen (max. 8 Sätze). Sag zuerst in einem Satz, was für ein Dokument es ist.\n\nDOKUMENT:\n{doc}",
    "prompt.sumMap": "Fasse den folgenden Dokumentabschnitt in 3-5 Stichpunkten zusammen. Nur die Stichpunkte, keine Einleitung.\n\nABSCHNITT:\n{teil}",
    "prompt.sumReduce": "Hier sind Stichpunkt-Zusammenfassungen der Teile eines Dokuments. Mach daraus EINE zusammenhängende Gesamtzusammenfassung in einfachem Deutsch (max. 10 Sätze). Sag zuerst, was für ein Dokument es ist.\n\nSTICHPUNKTE:\n{punkte}",
    "prompt.risk": "Analysiere das folgende Dokument. Liste auf, worauf man besonders achten muss:\n1. Fristen und Termine\n2. Kosten und Zahlungspflichten\n3. Kündigungs- oder Widerrufsregeln\n4. Ungewöhnliche oder nachteilige Klauseln\nZitiere kurz die relevante Stelle. Wenn zu einem Punkt nichts im Text steht, schreibe \"Nichts gefunden\".\n\nDOKUMENT:\n{doc}",
    "prompt.q": "Beantworte die Frage NUR anhand der folgenden Dokument-Auszüge. Wenn die Antwort dort nicht steht, sage das.\n\nAUSZÜGE:\n{ctx}\n\nFRAGE: {frage}",
    "prompt.routine": "{anweisung}\nZitiere kurz die relevanten Stellen. Wenn nichts im Text steht, schreibe \"Nichts gefunden\".\n\nDOKUMENT:\n{doc}",
    "prompt.transSys": "Du bist ein präziser Übersetzer. Übersetze den gegebenen Text vollständig nach {ziel}. Gib NUR die Übersetzung aus, ohne Kommentare oder Erklärungen.",
  },

  /* ================= ENGLISH ================= */
  en: {
    "html.title": "DokuCheck Local — AI document analysis without the cloud",
    "proof.mode": "LOCAL MODE",
    "proof.model": "Model download (one-time):",
    "proof.requests": "requests",
    "proof.analysis": "External requests during analysis:",
    "proof.ok": "Your documents never leave this device.",
    "proof.alert": "Warning: external network activity detected!",

    "hero.eyebrow": "Sovereign AI · Runs in your browser",
    "hero.lede": "Upload a contract, an official letter, or a photo of a document. A small AI reads, analyzes and translates everything right on your device — no server, no cloud account. Check it yourself: open DevTools (F12 → Network) during the analysis.",

    "gpu.title": "WebGPU not available",
    "gpu.intro": "The AI analysis needs WebGPU. Here's how to get it:",
    "gpu.desktop": "Desktop: use Chrome or Edge version 113 or newer; check the status at chrome://gpu or edge://gpu.",
    "gpu.android": "Android: Chrome version 121 or newer (Android 12+).",
    "gpu.ios": "iPhone/iPad: Safari from iOS 18 with WebGPU enabled.",
    "gpu.ocrNote": "Text recognition (OCR) from photos still works — it runs on any device.",
    "gpu.okBadge": "WebGPU available ✓",
    "gpu.missingBadge": "No WebGPU — analysis disabled, OCR still works.",

    "s1.tag": "Step 1",
    "s1.title": "Load the AI model onto your device",
    "s1.modelLabel": "Model:",
    "s1.m1": "Llama 3.2 1B — lightweight, works on phones (~0.8 GB)",
    "s1.m2": "Qwen3 1.7B — fast, good German (~1.2 GB)",
    "s1.m3": "Llama 3.2 3B — balanced, needs more memory (~2 GB)",
    "s1.loadBtn": "Load model",
    "s1.switchBtn": "Switch model",
    "s1.hint": "One-time download — stored in your browser. After that, analysis works offline too.",
    "s1.cached": "This model is already on your device — loading needs no download.",
    "s1.ready": "Model ready — the network proof counter is now armed.",
    "s1.error": "Loading failed:",

    "s2.tag": "Step 2",
    "s2.title": "Pick a document",
    "drop.title": "Drag a PDF, text file or photo here",
    "drop.or": "or tap to choose one.",
    "drop.note": "Everything happens locally — the file is never sent anywhere.",
    "camera.btn": "📷 Take a photo (OCR)",
    "ocr.l1": "OCR: German + English",
    "ocr.l2": "OCR: German only",
    "ocr.l3": "OCR: Vietnamese",
    "ocr.l4": "OCR: German + English + Vietnamese",
    "ocr.running": "Reading the text …",
    "ocr.done": "Text recognition done (locally on your device).",
    "ocr.none": "No text found — try a sharper, straighter photo.",
    "ocr.error": "OCR error:",
    "file.reading": "Reading:",
    "file.error": "Could not read the file:",
    "file.chars": "characters",
    "file.sections": "sections (processed locally)",
    "file.fromMemory": "loaded from memory",

    "s3.tag": "Step 3",
    "s3.title": "Analyze & translate",
    "btn.sum": "Summarize",
    "btn.risk": "What should I watch out for?",
    "btn.trans": "Translate",
    "btn.stop": "Stop",
    "btn.ask": "Ask",
    "lang.de": "German",
    "lang.en": "English",
    "lang.vi": "Vietnamese",
    "out.placeholder": "The analysis will show up here once the model and a document are ready.",
    "qa.placeholder": "Ask your own question about the document …",
    "disclaimer": "Note: DokuCheck Local gives you a first assessment from a small AI — it is not legal advice. For important contracts and deadlines, please talk to a lawyer or an advice center. Small models can make mistakes — always double-check important statements in the original text.",
    "err.prefix": "Error:",

    "mem.tag": "🧠 Memory",
    "mem.title": "What DokuCheck remembers — locally in your browser",
    "mem.analysen": "Analysis history",
    "mem.dokumente": "Saved documents",
    "mem.routinen": "Check routines",
    "mem.emptyAnalysen": "No analyses yet.",
    "mem.emptyDokumente": "No documents yet.",
    "mem.emptyRoutinen": "No routines yet.",
    "mem.show": "Show",
    "mem.open": "Open",
    "mem.run": "Run",
    "mem.edit": "Edit",
    "mem.delete": "Delete",
    "mem.save": "Save",
    "mem.export": "Export",
    "mem.import": "Import",
    "mem.namePh": "Name, e.g. “Rent check”",
    "mem.promptPh": "Instruction, e.g. “Check notice periods and extra costs …”",
    "mem.note": "Working memory = current document & session · Tool memory = remembered model and language choice. Everything lives in your browser's IndexedDB — none of it leaves your device.",
    "mem.imported": "routine(s) imported.",
    "mem.importFailed": "Import failed:",

    "action.sum": "Summary",
    "action.risk": "Risk check",
    "action.q": "Question",
    "action.trans": "Translation",
    "action.routine": "Routine:",
    "status.sumPart": "Summarizing part {i}/{n} …",
    "note.sumLong": "(Note: this document is very long — the first {max} of {n} parts were used.)",
    "note.transLong": "(Note: very long document — the first {max} of {n} sections were translated.)",

    "step.ready": "✓ ready",
    "hint.needModel": "Your document is ready ✓ — now load the AI model in step 1 and you're good to go.",
    "hint.goStep3": "All set ✓ — continue with step 3: analyze & translate.",
    "pdf.scanned": "Scanned PDF detected (no text layer) — running text recognition …",
    "pdf.ocrPage": "page {i}/{n} …",
    "pdf.noText": "No readable text found. Check the OCR language or try a sharper photo/PDF.",
    "pdf.limited": "(Note: only the first {n} pages were read via OCR.)",

    "footer": "DokuCheck Local v0.2 · Tech: WebLLM 0.2.79 (MLC AI, Apache 2.0) + WebGPU · Tesseract.js 5.1.1 (OCR) + pdf.js 4.4.168 — all libraries bundled locally, no CDN calls. Part of the Edge Cognitive AI Platform.",

    "prompt.sys": "You are a careful assistant who explains documents in plain, friendly language. Answer in English, clearly and briefly. Never make things up: if something is not in the text, say so explicitly.",
    "prompt.sumShort": "Summarize the following document in plain English (max 8 sentences). Start with one sentence saying what kind of document it is.\n\nDOCUMENT:\n{doc}",
    "prompt.sumMap": "Summarize the following document section in 3-5 bullet points. Only the bullets, no introduction.\n\nSECTION:\n{teil}",
    "prompt.sumReduce": "Here are bullet-point summaries of the parts of a document. Turn them into ONE coherent overall summary in plain English (max 10 sentences). Start by saying what kind of document it is.\n\nBULLETS:\n{punkte}",
    "prompt.risk": "Analyze the following document. List what the reader should watch out for:\n1. Deadlines and dates\n2. Costs and payment obligations\n3. Cancellation or withdrawal rules\n4. Unusual or disadvantageous clauses\nBriefly quote the relevant passage. If nothing is in the text for a point, write \"Nothing found\".\n\nDOCUMENT:\n{doc}",
    "prompt.q": "Answer the question ONLY based on the following document excerpts. If the answer is not there, say so.\n\nEXCERPTS:\n{ctx}\n\nQUESTION: {frage}",
    "prompt.routine": "{anweisung}\nBriefly quote the relevant passages. If nothing is in the text, write \"Nothing found\".\n\nDOCUMENT:\n{doc}",
    "prompt.transSys": "You are a precise translator. Translate the given text completely into {ziel}. Output ONLY the translation, no comments or explanations.",
  },

  /* ================= TIẾNG VIỆT ================= */
  vi: {
    "html.title": "DokuCheck Local — Phân tích tài liệu bằng AI, không cần đám mây",
    "proof.mode": "CHẾ ĐỘ CỤC BỘ",
    "proof.model": "Tải mô hình (một lần):",
    "proof.requests": "yêu cầu",
    "proof.analysis": "Yêu cầu ra ngoài khi phân tích:",
    "proof.ok": "Tài liệu của bạn không bao giờ rời khỏi thiết bị này.",
    "proof.alert": "Cảnh báo: phát hiện hoạt động mạng ra bên ngoài!",

    "hero.eyebrow": "AI tự chủ · Chạy ngay trong trình duyệt của bạn",
    "hero.lede": "Tải lên hợp đồng, thư từ cơ quan hoặc ảnh chụp tài liệu. Một mô hình AI nhỏ sẽ đọc, phân tích và dịch tất cả ngay trên thiết bị của bạn — không máy chủ, không tài khoản đám mây. Bạn tự kiểm tra được: mở DevTools (F12 → Network) trong lúc phân tích.",

    "gpu.title": "WebGPU không khả dụng",
    "gpu.intro": "Phần phân tích AI cần WebGPU. Cách bật:",
    "gpu.desktop": "Máy tính: dùng Chrome hoặc Edge từ phiên bản 113; kiểm tra tại chrome://gpu hoặc edge://gpu.",
    "gpu.android": "Android: Chrome từ phiên bản 121 (Android 12 trở lên).",
    "gpu.ios": "iPhone/iPad: Safari từ iOS 18 có bật WebGPU.",
    "gpu.ocrNote": "Nhận dạng chữ (OCR) từ ảnh vẫn hoạt động — chạy được trên mọi thiết bị.",
    "gpu.okBadge": "WebGPU sẵn sàng ✓",
    "gpu.missingBadge": "Không có WebGPU — phân tích bị tắt, OCR vẫn chạy.",

    "s1.tag": "Bước 1",
    "s1.title": "Tải mô hình AI về thiết bị của bạn",
    "s1.modelLabel": "Mô hình:",
    "s1.m1": "Llama 3.2 1B — nhẹ, chạy được trên điện thoại (~0,8 GB)",
    "s1.m2": "Qwen3 1.7B — nhanh, tiếng Đức tốt (~1,2 GB)",
    "s1.m3": "Llama 3.2 3B — cân bằng, cần nhiều bộ nhớ hơn (~2 GB)",
    "s1.loadBtn": "Tải mô hình",
    "s1.switchBtn": "Đổi mô hình",
    "s1.hint": "Chỉ tải một lần — được lưu trong trình duyệt. Sau đó phân tích chạy được cả khi offline.",
    "s1.cached": "Mô hình này đã có trên thiết bị — mở lên không cần tải lại.",
    "s1.ready": "Mô hình sẵn sàng — bộ đếm mạng bắt đầu hoạt động từ bây giờ.",
    "s1.error": "Lỗi khi tải:",

    "s2.tag": "Bước 2",
    "s2.title": "Chọn tài liệu",
    "drop.title": "Kéo file PDF, file chữ hoặc ảnh vào đây",
    "drop.or": "hoặc bấm để chọn.",
    "drop.note": "Mọi thứ diễn ra trên máy bạn — file không được gửi đi đâu cả.",
    "camera.btn": "📷 Chụp ảnh (OCR)",
    "ocr.l1": "OCR: tiếng Đức + tiếng Anh",
    "ocr.l2": "OCR: chỉ tiếng Đức",
    "ocr.l3": "OCR: tiếng Việt",
    "ocr.l4": "OCR: Đức + Anh + Việt",
    "ocr.running": "Đang nhận dạng chữ …",
    "ocr.done": "Nhận dạng xong (ngay trên thiết bị của bạn).",
    "ocr.none": "Không thấy chữ — thử chụp ảnh rõ nét và thẳng hơn nhé.",
    "ocr.error": "Lỗi OCR:",
    "file.reading": "Đang đọc:",
    "file.error": "Không đọc được file:",
    "file.chars": "ký tự",
    "file.sections": "đoạn (xử lý cục bộ)",
    "file.fromMemory": "mở từ bộ nhớ",

    "s3.tag": "Bước 3",
    "s3.title": "Phân tích & dịch",
    "btn.sum": "Tóm tắt",
    "btn.risk": "Cần chú ý điều gì?",
    "btn.trans": "Dịch",
    "btn.stop": "Dừng",
    "btn.ask": "Hỏi",
    "lang.de": "tiếng Đức",
    "lang.en": "tiếng Anh",
    "lang.vi": "tiếng Việt",
    "out.placeholder": "Kết quả phân tích sẽ hiện ở đây khi mô hình và tài liệu sẵn sàng.",
    "qa.placeholder": "Đặt câu hỏi của bạn về tài liệu …",
    "disclaimer": "Lưu ý: DokuCheck Local chỉ đưa ra đánh giá ban đầu từ một mô hình AI nhỏ — đây không phải tư vấn pháp lý. Với hợp đồng và thời hạn quan trọng, hãy hỏi luật sư hoặc trung tâm tư vấn. Mô hình nhỏ có thể sai — luôn kiểm tra lại các thông tin quan trọng trong văn bản gốc.",
    "err.prefix": "Lỗi:",

    "mem.tag": "🧠 Bộ nhớ",
    "mem.title": "DokuCheck ghi nhớ gì — lưu cục bộ trong trình duyệt của bạn",
    "mem.analysen": "Lịch sử phân tích",
    "mem.dokumente": "Tài liệu đã lưu",
    "mem.routinen": "Quy trình kiểm tra",
    "mem.emptyAnalysen": "Chưa có phân tích nào.",
    "mem.emptyDokumente": "Chưa có tài liệu nào.",
    "mem.emptyRoutinen": "Chưa có quy trình nào.",
    "mem.show": "Xem",
    "mem.open": "Mở",
    "mem.run": "Chạy",
    "mem.edit": "Sửa",
    "mem.delete": "Xóa",
    "mem.save": "Lưu",
    "mem.export": "Xuất",
    "mem.import": "Nhập",
    "mem.namePh": "Tên, ví dụ: “Kiểm tra hợp đồng thuê nhà”",
    "mem.promptPh": "Yêu cầu, ví dụ: “Kiểm tra thời hạn hủy và chi phí phụ …”",
    "mem.note": "Working memory = tài liệu & phiên hiện tại · Tool memory = ghi nhớ mô hình và ngôn ngữ đã chọn. Tất cả nằm trong IndexedDB của trình duyệt — không gì rời khỏi thiết bị của bạn.",
    "mem.imported": "quy trình đã được nhập.",
    "mem.importFailed": "Nhập thất bại:",

    "action.sum": "Tóm tắt",
    "action.risk": "Kiểm tra rủi ro",
    "action.q": "Câu hỏi",
    "action.trans": "Bản dịch",
    "action.routine": "Quy trình:",
    "status.sumPart": "Đang tóm tắt phần {i}/{n} …",
    "note.sumLong": "(Lưu ý: tài liệu rất dài — chỉ dùng {max} phần đầu trong tổng số {n} phần.)",
    "note.transLong": "(Lưu ý: tài liệu rất dài — chỉ dịch {max} đoạn đầu trong tổng số {n} đoạn.)",

    "step.ready": "✓ sẵn sàng",
    "hint.needModel": "Tài liệu đã sẵn sàng ✓ — giờ hãy tải mô hình AI ở Bước 1 là bắt đầu được ngay.",
    "hint.goStep3": "Xong hết rồi ✓ — tiếp tục với Bước 3: phân tích & dịch.",
    "pdf.scanned": "Phát hiện PDF scan (không có lớp chữ) — đang nhận dạng chữ …",
    "pdf.ocrPage": "trang {i}/{n} …",
    "pdf.noText": "Không đọc được chữ nào. Hãy kiểm tra ngôn ngữ OCR hoặc thử ảnh/PDF rõ nét hơn.",
    "pdf.limited": "(Lưu ý: chỉ đọc OCR {n} trang đầu.)",

    "footer": "DokuCheck Local v0.2 · Công nghệ: WebLLM 0.2.79 (MLC AI, Apache 2.0) + WebGPU · Tesseract.js 5.1.1 (OCR) + pdf.js 4.4.168 — mọi thư viện được đóng gói cục bộ, không gọi CDN. Thuộc Edge Cognitive AI Platform.",

    "prompt.sys": "Bạn là một trợ lý cẩn thận, giải thích tài liệu bằng ngôn ngữ thân thiện, dễ hiểu. Hãy trả lời bằng tiếng Việt, rõ ràng và ngắn gọn. Không được bịa: nếu thông tin không có trong văn bản, hãy nói rõ điều đó.",
    "prompt.sumShort": "Hãy tóm tắt tài liệu sau bằng tiếng Việt dễ hiểu (tối đa 8 câu). Câu đầu tiên hãy nói đây là loại tài liệu gì.\n\nTÀI LIỆU:\n{doc}",
    "prompt.sumMap": "Tóm tắt đoạn tài liệu sau thành 3-5 gạch đầu dòng. Chỉ gạch đầu dòng, không mở bài.\n\nĐOẠN:\n{teil}",
    "prompt.sumReduce": "Đây là các tóm tắt gạch đầu dòng của từng phần một tài liệu. Hãy viết MỘT bản tóm tắt tổng hợp mạch lạc bằng tiếng Việt dễ hiểu (tối đa 10 câu). Câu đầu hãy nói đây là loại tài liệu gì.\n\nGẠCH ĐẦU DÒNG:\n{punkte}",
    "prompt.risk": "Phân tích tài liệu sau. Liệt kê những điểm người đọc cần chú ý:\n1. Thời hạn và ngày quan trọng\n2. Chi phí và nghĩa vụ thanh toán\n3. Quy định hủy hoặc rút lui\n4. Điều khoản bất thường hoặc bất lợi\nTrích ngắn gọn đoạn liên quan. Nếu không có thông tin cho mục nào, ghi \"Không tìm thấy\".\n\nTÀI LIỆU:\n{doc}",
    "prompt.q": "CHỈ dựa vào các trích đoạn tài liệu sau để trả lời câu hỏi. Nếu không có câu trả lời trong đó, hãy nói rõ.\n\nTRÍCH ĐOẠN:\n{ctx}\n\nCÂU HỎI: {frage}",
    "prompt.routine": "{anweisung}\nTrích ngắn gọn các đoạn liên quan. Nếu không có gì trong văn bản, ghi \"Không tìm thấy\".\n\nTÀI LIỆU:\n{doc}",
    "prompt.transSys": "Bạn là một dịch giả chính xác. Hãy dịch toàn bộ văn bản sang {ziel}. CHỈ xuất bản dịch, không bình luận hay giải thích.",
  },
};

let sprache = "de";

export function t(key, vars) {
  let s = UEBERSETZUNGEN[sprache][key] ?? UEBERSETZUNGEN.de[key] ?? key;
  if (vars) for (const k of Object.keys(vars)) s = s.replaceAll("{" + k + "}", vars[k]);
  return s;
}

export function getLang() {
  return sprache;
}

/* Alle statischen Texte im DOM aktualisieren:
   data-i18n → textContent, data-i18n-ph → placeholder */
export function applyI18n() {
  document.documentElement.lang = sprache;
  document.title = t("html.title");
  for (const el of document.querySelectorAll("[data-i18n]")) {
    el.textContent = t(el.getAttribute("data-i18n"));
  }
  for (const el of document.querySelectorAll("[data-i18n-ph]")) {
    el.placeholder = t(el.getAttribute("data-i18n-ph"));
  }
  for (const btn of document.querySelectorAll(".lang-btn")) {
    btn.classList.toggle("active", btn.dataset.lang === sprache);
  }
}

export function setLang(l) {
  if (!UEBERSETZUNGEN[l]) return;
  sprache = l;
  sessionSet("sprache", l).catch(() => {});
  applyI18n();
  document.dispatchEvent(new CustomEvent("langchange"));
}

/* Beim Start: gemerkte Wahl (Tool Memory), sonst Browsersprache, sonst Deutsch */
export async function initLang() {
  let l;
  try { l = await sessionGet("sprache"); } catch { /* IndexedDB fehlt */ }
  if (!l || !UEBERSETZUNGEN[l]) {
    const nav = (navigator.language || "de").toLowerCase();
    l = nav.startsWith("vi") ? "vi" : nav.startsWith("en") ? "en" : "de";
  }
  sprache = l;
  applyI18n();
}
