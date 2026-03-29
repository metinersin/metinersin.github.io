const REQUIRED_STUDENT_COLUMNS = 3;
const ORDER_COLUMN_HEADER = "Math No";

const textCollator = new Intl.Collator("tr", {
  sensitivity: "base",
  ignorePunctuation: true
});

const idCollator = new Intl.Collator("tr", {
  sensitivity: "base",
  numeric: true
});

function toText(value) {
  if (value === null || value === undefined) {
    return "";
  }

  return String(value).trim();
}

function isRowEmpty(row) {
  return row.every((cell) => toText(cell) === "");
}

function normalizeHeaderRow(rawHeader, columnCount) {
  return Array.from({ length: columnCount }, (_, index) => {
    const headerValue = toText(rawHeader[index]);
    return headerValue || `Column ${index + 1}`;
  });
}

function normalizeDataRows(rawRows, columnCount) {
  return rawRows
    .filter((row) => !isRowEmpty(row))
    .map((row) => Array.from({ length: columnCount }, (_, index) => row[index] ?? ""));
}

function validateRows(rows) {
  const issues = [];
  const duplicateIds = new Set();
  const knownIds = new Set();

  rows.forEach((row, index) => {
    const rowNumber = index + 2;
    const name = toText(row[0]);
    const surname = toText(row[1]);
    const id = toText(row[2]);

    if (!name || !surname || !id) {
      issues.push(`Row ${rowNumber} is missing a name, surname, or student ID.`);
      return;
    }

    if (knownIds.has(id)) {
      duplicateIds.add(id);
      return;
    }

    knownIds.add(id);
  });

  if (issues.length > 0) {
    throw new Error(issues.slice(0, 3).join(" "));
  }

  if (duplicateIds.size > 0) {
    throw new Error(
      `Duplicate student IDs were found: ${Array.from(duplicateIds).slice(0, 5).join(", ")}.`
    );
  }
}

function compareStudentRows(left, right) {
  return (
    textCollator.compare(toText(left.row[1]), toText(right.row[1])) ||
    textCollator.compare(toText(left.row[0]), toText(right.row[0])) ||
    idCollator.compare(toText(left.row[2]), toText(right.row[2])) ||
    left.originalIndex - right.originalIndex
  );
}

function calculateColumnWidths(rows) {
  const columnCount = rows.reduce((largest, row) => Math.max(largest, row.length), 0);

  return Array.from({ length: columnCount }, (_, columnIndex) => {
    const minWidth = columnIndex === 0 ? 4 : 10;
    const padding = columnIndex === 0 ? 1 : 2;
    const width = rows.reduce((largest, row) => {
      const value = row[columnIndex] ?? "";
      return Math.max(largest, toText(value).length);
    }, 0);

    return { wch: Math.min(Math.max(width + padding, minWidth), 36) };
  });
}

function buildWorksheet(XLSX, headerRow, students) {
  const rows = [
    [ORDER_COLUMN_HEADER, ...headerRow],
    ...students.map((student) => [student.order, ...student.row])
  ];
  const worksheet = XLSX.utils.aoa_to_sheet(rows);
  worksheet["!cols"] = calculateColumnWidths(rows);
  return worksheet;
}

export function buildStudentDataset(rawRows) {
  if (rawRows.length === 0) {
    throw new Error("The uploaded workbook is empty.");
  }

  const [rawHeader = [], ...rawDataRows] = rawRows;
  const columnCount = Math.max(
    REQUIRED_STUDENT_COLUMNS,
    rawHeader.length,
    ...rawDataRows.map((row) => row.length)
  );

  const headerRow = normalizeHeaderRow(rawHeader, columnCount);
  const studentRows = normalizeDataRows(rawDataRows, columnCount);

  if (studentRows.length === 0) {
    throw new Error("No student rows were found after the header row.");
  }

  validateRows(studentRows);

  const students = studentRows
    .map((row, originalIndex) => ({ row, originalIndex }))
    .sort(compareStudentRows)
    .map((student, index) => ({
      ...student,
      order: index + 1
    }));

  return {
    headerRow,
    students
  };
}

export function assignStudentsToClassrooms(students, classroomNames, capacities) {
  let cursor = 0;

  const classrooms = classroomNames.map((name, index) => {
    const capacity = capacities[index];
    const assignedStudents = students.slice(cursor, cursor + capacity);
    cursor += assignedStudents.length;

    return {
      name,
      capacity,
      students: assignedStudents
    };
  });

  const overflow = {
    name: "Left Out Students",
    capacity: null,
    students: students.slice(cursor)
  };

  return {
    classrooms,
    overflow,
    totalStudents: students.length,
    totalCapacity: capacities.reduce((sum, value) => sum + value, 0)
  };
}

export function buildWorkbook(XLSX, headerRow, assignment) {
  const workbook = XLSX.utils.book_new();

  assignment.classrooms.forEach((classroom) => {
    if (classroom.students.length === 0) {
      return;
    }

    const worksheet = buildWorksheet(XLSX, headerRow, classroom.students);
    XLSX.utils.book_append_sheet(workbook, worksheet, classroom.name);
  });

  if (assignment.overflow.students.length > 0) {
    const overflowWorksheet = buildWorksheet(XLSX, headerRow, assignment.overflow.students);
    XLSX.utils.book_append_sheet(workbook, overflowWorksheet, assignment.overflow.name);
  }

  return workbook;
}
