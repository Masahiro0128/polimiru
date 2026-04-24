/**
 * 吉村洋文 2023年公約レビューシート セットアップスクリプト
 *
 * 使い方:
 *   1. Googleスプレッドシートを開く
 *   2. 拡張機能 → Apps Script
 *   3. このコードを貼り付けて「実行」ボタンを押す
 */

function setupReviewSheet() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getActiveSheet();

  // ヘッダー行を探す（「達成状況」列のインデックスを特定）
  const headerRow = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const colIndex = {
    status:      headerRow.indexOf("達成状況") + 1,
    evidenceUrl: headerRow.indexOf("証拠URL") + 1,
    level:       headerRow.indexOf("レベル") + 1,
    score:       headerRow.indexOf("具体性スコア") + 1,
    kpi:         headerRow.indexOf("KPIあり") + 1,
    deadline:    headerRow.indexOf("期限あり") + 1,
    process:     headerRow.indexOf("手段あり") + 1,
    text:        headerRow.indexOf("公約テキスト") + 1,
  };

  const lastRow = sheet.getLastRow();
  const dataRange = sheet.getRange(2, colIndex.status, lastRow - 1, 1);

  // ── 1. 達成状況 ドロップダウン ──────────────────────────
  const rule = SpreadsheetApp.newDataValidation()
    .requireValueInList(["完了", "着手", "未着手", "不明"], true)
    .setAllowInvalid(false)
    .setHelpText("完了 / 着手 / 未着手 / 不明 から選択してください")
    .build();
  dataRange.setDataValidation(rule);

  // ── 2. 条件付き書式（行全体の背景色） ───────────────────
  const fullRowRange = sheet.getRange(2, 1, lastRow - 1, sheet.getLastColumn());
  const rules = sheet.getConditionalFormatRules();

  const statusCol = columnLetter(colIndex.status);

  // 完了 → 緑
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(`=$${statusCol}2="完了"`)
    .setBackground("#d9ead3")
    .setRanges([fullRowRange])
    .build());

  // 着手 → 黄
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(`=$${statusCol}2="着手"`)
    .setBackground("#fff2cc")
    .setRanges([fullRowRange])
    .build());

  // 未着手 → 薄赤
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(`=$${statusCol}2="未着手"`)
    .setBackground("#fce5cd")
    .setRanges([fullRowRange])
    .build());

  // 不明 → 薄灰
  rules.push(SpreadsheetApp.newConditionalFormatRule()
    .whenFormulaSatisfied(`=$${statusCol}2="不明"`)
    .setBackground("#efefef")
    .setRanges([fullRowRange])
    .build());

  sheet.setConditionalFormatRules(rules);

  // ── 3. ヘッダー行を固定・太字 ───────────────────────────
  sheet.setFrozenRows(1);
  sheet.getRange(1, 1, 1, sheet.getLastColumn())
    .setFontWeight("bold")
    .setBackground("#4a86e8")
    .setFontColor("#ffffff");

  // ── 4. 列幅を調整 ────────────────────────────────────────
  sheet.setColumnWidth(colIndex.text, 400);
  if (colIndex.evidenceUrl > 0) sheet.setColumnWidth(colIndex.evidenceUrl, 250);
  sheet.autoResizeColumns(1, colIndex.text - 1);

  // ── 5. 進捗サマリーを別シートに追加 ─────────────────────
  let summarySheet = ss.getSheetByName("📊 進捗サマリー");
  if (!summarySheet) {
    summarySheet = ss.insertSheet("📊 進捗サマリー");
  }
  setupSummarySheet(summarySheet, sheet.getName(), colIndex, lastRow);

  SpreadsheetApp.getUi().alert(
    "✅ セットアップ完了！\n\n" +
    "・「達成状況」列にドロップダウンを追加しました\n" +
    "・行の背景色が達成状況に応じて自動変化します\n" +
    "・「📊 進捗サマリー」シートを追加しました"
  );
}


function setupSummarySheet(summarySheet, dataSheetName, colIndex, lastRow) {
  summarySheet.clearContents();

  const statusCol = columnLetter(colIndex.status);
  const catCol    = columnLetter(headerColByName(dataSheetName, "カテゴリ") || 7);

  const data = [
    ["📊 公約達成率サマリー", ""],
    ["", ""],
    ["項目", "件数"],
    ["総公約数",    `=COUNTA('${dataSheetName}'!A2:A1000)-1`],
    ["レビュー済", `=COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"完了")+COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"着手")+COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"未着手")`],
    ["完了",       `=COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"完了")`],
    ["着手中",     `=COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"着手")`],
    ["未着手",     `=COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"未着手")`],
    ["不明",       `=COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"不明")`],
    ["未レビュー", `=COUNTA('${dataSheetName}'!A2:A1000)-1-COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"完了")-COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"着手")-COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"未着手")-COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"不明")`],
    ["", ""],
    ["達成スコア（完了+着手×0.5）/ 総数", `=IFERROR(ROUND((COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"完了")+COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"着手")*0.5)/(COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"完了")+COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"着手")+COUNTIF('${dataSheetName}'!$${statusCol}2:$${statusCol}1000,"未着手"))*100,1)&" / 100","未レビュー")`],
  ];

  summarySheet.getRange(1, 1, data.length, 2).setValues(data);
  summarySheet.getRange(1, 1).setFontSize(16).setFontWeight("bold");
  summarySheet.getRange(3, 1, 1, 2).setFontWeight("bold").setBackground("#4a86e8").setFontColor("#ffffff");
  summarySheet.setColumnWidth(1, 300);
  summarySheet.setColumnWidth(2, 120);
}


function columnLetter(colNum) {
  let letter = "";
  while (colNum > 0) {
    const mod = (colNum - 1) % 26;
    letter = String.fromCharCode(65 + mod) + letter;
    colNum = Math.floor((colNum - 1) / 26);
  }
  return letter;
}

function headerColByName(sheetName, colName) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  if (!sheet) return null;
  const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
  const idx = headers.indexOf(colName);
  return idx >= 0 ? idx + 1 : null;
}
