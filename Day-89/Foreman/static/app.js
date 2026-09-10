const board = document.getElementById("board");
const columnBodies = document.querySelectorAll(".column-body");

const modalOverlay = document.getElementById("modal-overlay");
const modalTitle = document.getElementById("modal-title");
const taskForm = document.getElementById("task-form");
const fieldId = document.getElementById("task-id");
const fieldTitle = document.getElementById("field-title");
const fieldDescription = document.getElementById("field-description");
const fieldPriority = document.getElementById("field-priority");
const fieldStatus = document.getElementById("field-status");
const deleteBtn = document.getElementById("delete-task-btn");
const saveBtn = document.getElementById("save-btn");

let draggingId = null;

// ---------- Rendering ----------

function priorityLabel(priority) {
  return { low: "Low", medium: "Medium", high: "High" }[priority] || priority;
}

function buildCard(task) {
  const card = document.createElement("article");
  card.className = "card";
  card.draggable = true;
  card.dataset.id = task.id;
  card.dataset.priority = task.priority;

  card.innerHTML = `
    <div class="card-top">
      <span class="card-key">${task.key}</span>
      <span class="card-priority priority-${task.priority}">${priorityLabel(task.priority)}</span>
    </div>
    <h3 class="card-title"></h3>
    ${task.description ? `<p class="card-desc"></p>` : ""}
  `;
  card.querySelector(".card-title").textContent = task.title;
  if (task.description) {
    card.querySelector(".card-desc").textContent = task.description;
  }

  card.addEventListener("click", () => openEditModal(task));

  card.addEventListener("dragstart", () => {
    draggingId = task.id;
    card.classList.add("dragging");
  });
  card.addEventListener("dragend", () => {
    card.classList.remove("dragging");
    draggingId = null;
    persistAllColumns();
  });

  return card;
}

function renderBoard(tasks) {
  columnBodies.forEach((body) => (body.innerHTML = ""));

  const byStatus = { todo: [], doing: [], done: [] };
  tasks.forEach((t) => byStatus[t.status] && byStatus[t.status].push(t));
  Object.values(byStatus).forEach((list) => list.sort((a, b) => a.position - b.position));

  Object.entries(byStatus).forEach(([status, list]) => {
    const body = document.querySelector(`.column-body[data-dropzone="${status}"]`);
    list.forEach((task) => body.appendChild(buildCard(task)));
    document.querySelector(`.count[data-count="${status}"]`).textContent = list.length;
  });
}

async function loadTasks() {
  const res = await fetch("/api/tasks");
  const tasks = await res.json();
  renderBoard(tasks);
}

// ---------- Drag and drop ----------

function getDragAfterElement(container, y) {
  const cards = [...container.querySelectorAll(".card:not(.dragging)")];
  return cards.reduce(
    (closest, card) => {
      const box = card.getBoundingClientRect();
      const offset = y - box.top - box.height / 2;
      if (offset < 0 && offset > closest.offset) {
        return { offset, element: card };
      }
      return closest;
    },
    { offset: Number.NEGATIVE_INFINITY, element: null }
  ).element;
}

columnBodies.forEach((body) => {
  body.addEventListener("dragover", (e) => {
    e.preventDefault();
    const dragging = document.querySelector(".card.dragging");
    if (!dragging) return;
    const afterElement = getDragAfterElement(body, e.clientY);
    if (afterElement == null) {
      body.appendChild(dragging);
    } else {
      body.insertBefore(dragging, afterElement);
    }
  });
});

async function persistAllColumns() {
  const requests = [];
  columnBodies.forEach((body) => {
    const status = body.dataset.dropzone;
    const ids = [...body.querySelectorAll(".card")].map((c) => Number(c.dataset.id));
    requests.push(
      fetch("/api/reorder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status, ordered_ids: ids }),
      })
    );
  });
  await Promise.all(requests);
  updateCounts();
}

function updateCounts() {
  columnBodies.forEach((body) => {
    const status = body.dataset.dropzone;
    const count = body.querySelectorAll(".card").length;
    document.querySelector(`.count[data-count="${status}"]`).textContent = count;
  });
}

// ---------- Modal (add / edit) ----------

function openAddModal() {
  modalTitle.textContent = "New task";
  fieldId.value = "";
  fieldTitle.value = "";
  fieldDescription.value = "";
  fieldPriority.value = "medium";
  fieldStatus.value = "todo";
  deleteBtn.hidden = true;
  saveBtn.textContent = "Add task";
  modalOverlay.hidden = false;
  fieldTitle.focus();
}

function openEditModal(task) {
  modalTitle.textContent = task.key;
  fieldId.value = task.id;
  fieldTitle.value = task.title;
  fieldDescription.value = task.description || "";
  fieldPriority.value = task.priority;
  fieldStatus.value = task.status;
  deleteBtn.hidden = false;
  saveBtn.textContent = "Save changes";
  modalOverlay.hidden = false;
}

function closeModal() {
  modalOverlay.hidden = true;
}

document.getElementById("new-task-btn").addEventListener("click", openAddModal);
document.getElementById("cancel-btn").addEventListener("click", closeModal);
modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) closeModal();
});

taskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = fieldId.value;
  const payload = {
    title: fieldTitle.value.trim(),
    description: fieldDescription.value.trim(),
    priority: fieldPriority.value,
    status: fieldStatus.value,
  };
  if (!payload.title) return;

  if (id) {
    await fetch(`/api/tasks/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } else {
    await fetch("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  }
  closeModal();
  loadTasks();
});

deleteBtn.addEventListener("click", async () => {
  const id = fieldId.value;
  if (!id) return;
  if (!confirm("Delete this task?")) return;
  await fetch(`/api/tasks/${id}`, { method: "DELETE" });
  closeModal();
  loadTasks();
});

// ---------- Init ----------

loadTasks();
