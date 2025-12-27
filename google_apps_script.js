function syncToBackend(e) {
  if (!e) return;
  
  const sheet = e.source.getActiveSheet();
  const range = e.range;
  const startRow = range.getRow();
  const numRows = range.getNumRows();
  
  // Skip header row edits if they are the ONLY thing edited
  if (startRow === 1 && numRows === 1) return;

  const lastCol = sheet.getLastColumn();
  if (lastCol === 0) return;

  // Get headers for mapping
  const headers = sheet.getRange(1, 1, 1, lastCol).getValues()[0];
  
  // Get all values in the edited range (extending to all columns)
  // We grab from startRow to startRow + numRows - 1
  const dataRange = sheet.getRange(startRow, 1, numRows, lastCol);
  const values = dataRange.getValues();
  
  const updates = [];

  for (let i = 0; i < numRows; i++) {
    const currentRowIndex = startRow + i;
    
    // Skip header row if it's included in a multi-row edit
    if (currentRowIndex === 1) continue;

    const rowValues = values[i];
    const dataPayload = {};
    
    headers.forEach((header, index) => {
      // Use header name or fallback to col index
      const key = header ? header.toString() : `col${index+1}`;
      dataPayload[key] = rowValues[index];
    });

    updates.push({
      row: currentRowIndex,
      data: dataPayload,
      source: "SHEET"
    });
  }

  if (updates.length === 0) return;

  const payload = {
    updates: updates
  };

  // Replace with your actual public URL (e.g., ngrok)
  const API_URL = "https://preluxurious-sonny-superciliously.ngrok-free.dev/sync/batch-from-sheet";
  
  try {
    const options = {
      'method' : 'post',
      'contentType': 'application/json',
      'payload' : JSON.stringify(payload),
      'muteHttpExceptions': true
    };
    
    const response = UrlFetchApp.fetch(API_URL, options);
    if (response.getResponseCode() !== 200) {
      Logger.log("Sync failed: " + response.getContentText());
    }
  } catch (error) {
    Logger.log("Error sending to API: " + error.toString());
  }
}
