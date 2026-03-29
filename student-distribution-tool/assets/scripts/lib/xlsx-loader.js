const XLSX_SCRIPT_URL =
  "https://cdn.sheetjs.com/xlsx-0.20.3/package/dist/xlsx.full.min.js";

let xlsxPromise = null;

export function loadXlsxLibrary() {
  if (window.XLSX) {
    return Promise.resolve(window.XLSX);
  }

  if (!xlsxPromise) {
    xlsxPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");

      script.src = XLSX_SCRIPT_URL;
      script.async = true;
      script.addEventListener(
        "load",
        () => {
          if (window.XLSX) {
            resolve(window.XLSX);
            return;
          }

          reject(new Error("SheetJS loaded but the XLSX API is unavailable."));
        },
        { once: true }
      );
      script.addEventListener(
        "error",
        () => {
          reject(new Error("The Excel library could not be loaded."));
        },
        { once: true }
      );

      document.head.append(script);
    }).catch((error) => {
      xlsxPromise = null;
      throw error;
    });
  }

  return xlsxPromise;
}
