const API_BASE_URL = 'http://127.0.0.1:8000'; // Базовый URL вашего API

// Fetch glossary data from API
async function fetchGlossary() {
    const response = await fetch(`${API_BASE_URL}/terms/`);
    if (!response.ok) {
        throw new Error('Failed to fetch glossary data');
    }
    return response.json();
}

// Render glossary dynamically
async function renderGlossary() {
    const glossaryContent = document.getElementById("glossary-content");
    glossaryContent.innerHTML = '<p>Loading glossary...</p>'; // Показываем загрузку
    try {
        const glossary = await fetchGlossary();
        glossaryContent.innerHTML = ''; // Очищаем контейнер после загрузки данных

        glossary.forEach(item => {
            const div = document.createElement("div");
            div.className = "glossary-item";
            div.innerHTML = `<h3>${item.name}</h3><p>${item.description}</p>`;
            glossaryContent.appendChild(div);
        });
    } catch (error) {
        glossaryContent.innerHTML = '<p>Error loading glossary.</p>';
        console.error(error);
    }
}

// Fetch graph data from API
async function fetchGraphData() {
    const response = await fetch(`${API_BASE_URL}/graph`);
    return response.json();
}

// Render graph dynamically
async function drawGraph() {
    const graphDiv = document.getElementById("network");
    graphDiv.innerHTML = ''; // Очистка графа
    try {
        const data = await fetchGraphData();

        const nodes = new vis.DataSet(data.nodes.map(node => ({
            id: node.id,
            label: node.label,
            title: node.description
        })));

        const edges = new vis.DataSet(data.edges.map(edge => ({
            from: edge.from,
            to: edge.to,
            label: edge.relation
        })));

        const container = document.getElementById("network");
        const options = {
            interaction: { hover: true },
            edges: { arrows: "to", color: { color: "#848484", highlight: "#4CAF50" } },
            nodes: {
                shape: "box",
                size: 15,
                color: {
                    background: "#5BC0EB",
                    border: "#4CAF50"
                },
                font: {
                    size: 14,
                    color: "#FFFFFF"
                },
            },
            physics: { enabled: true, stabilization: { iterations: 100 } },
        };

        new vis.Network(container, { nodes, edges }, options);
    } catch (error) {
        graphDiv.innerHTML = '<p>Error loading graph.</p>';
        console.error(error);
    }
}

// Handle tab switching
const tabGlossary = document.getElementById("tab-glossary");
const tabGraph = document.getElementById("tab-graph");
const glossaryDiv = document.getElementById("glossary-content");
const graphDiv = document.getElementById("graph-content");

tabGlossary.addEventListener("click", () => {
    tabGlossary.classList.add("active");
    tabGraph.classList.remove("active");
    glossaryDiv.style.display = "flex";
    graphDiv.style.display = "none";
    renderGlossary(); // Рендерим глоссарий
});

tabGraph.addEventListener("click", () => {
    tabGraph.classList.add("active");
    tabGlossary.classList.remove("active");
    glossaryDiv.style.display = "none";
    graphDiv.style.display = "block";
    drawGraph(); // Рендерим граф
});

// Initial render
renderGlossary(); // По умолчанию загружается глоссарий
