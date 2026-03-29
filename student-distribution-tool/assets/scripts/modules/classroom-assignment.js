import { CLASSROOMS } from "../config/classrooms.js";
import { loadXlsxLibrary } from "../lib/xlsx-loader.js";
import {
  assignStudentsToClassrooms,
  buildStudentDataset,
  buildWorkbook
} from "../utils/classroom-assignment.js";

function updateStatus(statusElement, message, isError = false) {
  statusElement.textContent = message;
  statusElement.classList.toggle("status--error", Boolean(isError));
}

function createCapacityField(classroom, index) {
  const defaultCapacity = Number.isInteger(classroom.defaultCapacity) && classroom.defaultCapacity >= 0
    ? classroom.defaultCapacity
    : 0;
  const label = document.createElement("label");
  label.className = "capacity-field";

  const title = document.createElement("span");
  title.className = "capacity-field__name";
  title.textContent = classroom.name;

  const input = document.createElement("input");
  input.type = "number";
  input.min = "0";
  input.step = "1";
  input.inputMode = "numeric";
  input.value = String(defaultCapacity);
  input.placeholder = String(defaultCapacity);
  input.dataset.classroomIndex = String(index);
  input.setAttribute("aria-label", `${classroom.name} capacity`);

  label.append(title, input);
  return label;
}

function renderCapacityFields(container, classrooms) {
  const fragment = document.createDocumentFragment();

  classrooms.forEach((classroom, index) => {
    fragment.append(createCapacityField(classroom, index));
  });

  container.replaceChildren(fragment);
}

function parseCapacityValue(value) {
  const trimmedValue = value.trim();

  if (trimmedValue === "") {
    return 0;
  }

  const parsed = Number(trimmedValue);

  if (!Number.isInteger(parsed) || parsed < 0) {
    return null;
  }

  return parsed;
}

function readCapacities(capacityFields) {
  const capacities = [];

  for (const field of capacityFields) {
    const parsedValue = parseCapacityValue(field.value);

    if (parsedValue === null) {
      throw new Error("Every classroom capacity must be a whole number greater than or equal to 0.");
    }

    capacities.push(parsedValue);
  }

  return capacities;
}

function updateTotalCapacity(totalCapacityElement, capacityFields) {
  const total = Array.from(capacityFields).reduce((sum, field) => {
    const parsedValue = parseCapacityValue(field.value);
    return sum + (parsedValue ?? 0);
  }, 0);

  totalCapacityElement.textContent = String(total);
}

function readFirstWorksheetRows(XLSX, workbook) {
  const firstSheetName = workbook.SheetNames[0];

  if (!firstSheetName) {
    throw new Error("The uploaded workbook does not contain any worksheets.");
  }

  const firstWorksheet = workbook.Sheets[firstSheetName];

  return XLSX.utils.sheet_to_json(firstWorksheet, {
    header: 1,
    raw: false,
    defval: "",
    blankrows: false
  });
}

function buildDownloadFileName() {
  const today = new Date().toISOString().slice(0, 10);
  return `student-distribution-${today}.xlsx`;
}

function createWorkbookDownload(XLSX, workbook) {
  const workbookBuffer = XLSX.write(workbook, {
    bookType: "xlsx",
    type: "array"
  });

  const workbookBlob = new Blob([workbookBuffer], {
    type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  });

  return {
    fileName: buildDownloadFileName(),
    url: URL.createObjectURL(workbookBlob)
  };
}

function getDisplayedSurname(student) {
  if (!student) {
    return "-";
  }

  const surname = student.row[1];
  return surname ? String(surname) : "-";
}

function createSurnameRangeItem(labelText, surnameText) {
  const item = document.createElement("p");
  item.className = "distribution-card__range-item";

  const label = document.createElement("span");
  label.textContent = labelText;

  const value = document.createElement("strong");
  value.textContent = surnameText;

  item.append(label, value);
  return item;
}

function renderDistributionCard(classroom) {
  const card = document.createElement("article");
  card.className = "distribution-card";

  if (classroom.capacity === null) {
    card.classList.add("distribution-card--overflow");
  }

  const titleRow = document.createElement("div");
  titleRow.className = "distribution-card__title";

  const title = document.createElement("strong");
  title.textContent = classroom.name;

  const count = document.createElement("span");
  count.textContent = `${classroom.students.length} student(s)`;

  titleRow.append(title, count);

  const meta = document.createElement("p");
  meta.className = "distribution-card__meta";
  meta.textContent =
    classroom.capacity === null
      ? "Students who do not fit into the defined classroom capacities."
      : `Capacity: ${classroom.capacity}`;

  const surnameRange = document.createElement("div");
  surnameRange.className = "distribution-card__range";

  const firstSurname = createSurnameRangeItem(
    "First surname",
    getDisplayedSurname(classroom.students[0])
  );

  const lastSurname = createSurnameRangeItem(
    "Last surname",
    getDisplayedSurname(classroom.students[classroom.students.length - 1])
  );

  surnameRange.append(firstSurname, lastSurname);

  card.append(titleRow, meta, surnameRange);
  return card;
}

function renderAssignmentSummary(summaryElement, listElement, assignment) {
  document.getElementById("summary-total-students").textContent = String(assignment.totalStudents);
  document.getElementById("summary-total-capacity").textContent = String(assignment.totalCapacity);
  document.getElementById("summary-overflow-students").textContent = String(
    assignment.overflow.students.length
  );

  const cards = [
    ...assignment.classrooms
      .filter((classroom) => classroom.students.length > 0)
      .map(renderDistributionCard),
    renderDistributionCard(assignment.overflow)
  ];

  listElement.replaceChildren(...cards);
  summaryElement.hidden = false;
}

function triggerDownload(downloadState) {
  const anchor = document.createElement("a");
  anchor.href = downloadState.url;
  anchor.download = downloadState.fileName;
  anchor.click();
}

function getFileToken(file) {
  return `${file.name}:${file.size}:${file.lastModified}`;
}

async function loadStudentDataset(file) {
  const XLSX = await loadXlsxLibrary();
  const workbookBuffer = await file.arrayBuffer();
  const workbook = XLSX.read(workbookBuffer, { type: "array" });
  const rawRows = readFirstWorksheetRows(XLSX, workbook);
  return buildStudentDataset(rawRows);
}

export function initClassroomAssignment(root = document) {
  const form = root.getElementById("assignment-form");

  if (!form) {
    return;
  }

  const workbookInput = root.getElementById("student-workbook");
  const capacityContainer = root.getElementById("capacity-fields");
  const classroomCountLabel = root.getElementById("classroom-count");
  const totalCapacityElement = root.getElementById("total-capacity");
  const status = root.getElementById("assignment-status");
  const summary = root.getElementById("assignment-summary");
  const distributionList = root.getElementById("distribution-list");
  const downloadButton = root.getElementById("download-workbook");
  const studentCountNote = root.getElementById("student-count-note");
  const classroomNames = CLASSROOMS.map((classroom) => classroom.name);

  let currentDownload = null;
  let currentDataset = null;
  let currentDatasetToken = null;
  let pendingWorkbookToken = null;

  if (classroomCountLabel) {
    classroomCountLabel.textContent = String(CLASSROOMS.length);
  }

  function clearCurrentDownload() {
    if (currentDownload) {
      URL.revokeObjectURL(currentDownload.url);
      currentDownload = null;
    }

    downloadButton.hidden = true;
    downloadButton.disabled = true;
  }

  renderCapacityFields(capacityContainer, CLASSROOMS);

  const capacityFields = capacityContainer.querySelectorAll("input");
  updateTotalCapacity(totalCapacityElement, capacityFields);

  capacityContainer.addEventListener("input", () => {
    updateTotalCapacity(totalCapacityElement, capacityFields);
    summary.hidden = true;
    clearCurrentDownload();
  });

  workbookInput.addEventListener("change", () => {
    summary.hidden = true;
    clearCurrentDownload();
    currentDataset = null;
    currentDatasetToken = null;

    const selectedFile = workbookInput.files && workbookInput.files[0];

    if (!selectedFile) {
      pendingWorkbookToken = null;
      studentCountNote.textContent = "Detected students: 0";
      updateStatus(status, "Set capacities, upload a workbook, then prepare the classroom file.");
      return;
    }

    const selectedFileToken = getFileToken(selectedFile);
    pendingWorkbookToken = selectedFileToken;
    studentCountNote.textContent = "Detected students: reading workbook...";
    updateStatus(status, "Reading workbook...", false);

    loadStudentDataset(selectedFile)
      .then((dataset) => {
        if (pendingWorkbookToken !== selectedFileToken) {
          return;
        }

        currentDataset = dataset;
        currentDatasetToken = selectedFileToken;
        studentCountNote.textContent = `Detected students: ${dataset.students.length}`;
        updateStatus(
          status,
          `Workbook selected. ${dataset.students.length} student(s) found in the first worksheet.`,
          false
        );
      })
      .catch((error) => {
        if (pendingWorkbookToken !== selectedFileToken) {
          return;
        }

        studentCountNote.textContent = "Detected students: unavailable";
        updateStatus(status, error.message || "The workbook could not be read.", true);
      });
  });

  downloadButton.addEventListener("click", () => {
    if (!currentDownload) {
      return;
    }

    triggerDownload(currentDownload);
  });

  window.addEventListener("beforeunload", () => {
    clearCurrentDownload();
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const selectedFile = workbookInput.files && workbookInput.files[0];

    if (!selectedFile) {
      summary.hidden = true;
      updateStatus(status, "Choose an Excel workbook before preparing the classroom file.", true);
      return;
    }

    let capacities;

    try {
      capacities = readCapacities(capacityFields);
    } catch (error) {
      summary.hidden = true;
      updateStatus(status, error.message, true);
      return;
    }

    updateStatus(status, "Preparing workbook...", false);

    try {
      const dataset =
        currentDataset && currentDatasetToken === getFileToken(selectedFile)
          ? currentDataset
          : await loadStudentDataset(selectedFile);
      const assignment = assignStudentsToClassrooms(
        dataset.students,
        classroomNames,
        capacities
      );
      const XLSX = await loadXlsxLibrary();
      const outputWorkbook = buildWorkbook(XLSX, dataset.headerRow, assignment);
      clearCurrentDownload();
      currentDownload = createWorkbookDownload(XLSX, outputWorkbook);
      downloadButton.hidden = false;
      downloadButton.disabled = false;
      currentDataset = dataset;
      currentDatasetToken = getFileToken(selectedFile);
      studentCountNote.textContent = `Detected students: ${dataset.students.length}`;

      renderAssignmentSummary(summary, distributionList, assignment);
      updateStatus(
        status,
        `Workbook ready. Download the classroom file for ${assignment.totalStudents} student(s).`,
        false
      );
    } catch (error) {
      summary.hidden = true;
      downloadButton.hidden = true;
      downloadButton.disabled = true;
      updateStatus(status, error.message || "The workbook could not be prepared.", true);
    }
  });
}
