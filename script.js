const formulario = document.getElementById('formulario');
const mensagem = document.getElementById('mensagem');
const cancelar = document.getElementById('cancelar');
let produtos = [];

async function carregarCategorias() {
    const resposta = await fetch('/api/categorias');
    const categorias = await resposta.json();
    document.getElementById('categoria').innerHTML = categorias
        .map(c => `<option value="${c.Id}">${c.Nome}</option>`).join('');
}

async function carregarProdutos() {
    const resposta = await fetch('/api/produtos');
    produtos = await resposta.json();
    const lista = document.getElementById('lista-produtos');
    if (produtos.length === 0) {
        lista.innerHTML = '<tr><td colspan="6">Nenhum produto cadastrado.</td></tr>';
        return;
    }
    lista.innerHTML = produtos.map(p => `
        <tr>
            <td>${p.Id}</td><td>${p.Nome}</td><td>${p.Categoria}</td>
            <td>${p.Quantidade}</td><td>R$ ${Number(p.Preco).toFixed(2)}</td>
            <td>
                <button class="editar" onclick="editarProduto(${p.Id})">Editar</button>
                <button class="excluir" onclick="excluirProduto(${p.Id})">Excluir</button>
            </td>
        </tr>`).join('');
}

formulario.addEventListener('submit', async (evento) => {
    evento.preventDefault();
    const id = document.getElementById('produto-id').value;
    const dados = {
        nome: document.getElementById('nome').value,
        quantidade: document.getElementById('quantidade').value,
        preco: document.getElementById('preco').value,
        categoriaId: document.getElementById('categoria').value
    };
    const resposta = await fetch(id ? `/api/produtos/${id}` : '/api/produtos', {
        method: id ? 'PUT' : 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(dados)
    });
    const resultado = await resposta.json();
    mensagem.textContent = resultado.mensagem || resultado.erro;
    if (resposta.ok) {
        limparFormulario();
        carregarProdutos();
    }
});

function editarProduto(id) {
    const produto = produtos.find(p => p.Id === id);
    document.getElementById('produto-id').value = produto.Id;
    document.getElementById('nome').value = produto.Nome;
    document.getElementById('quantidade').value = produto.Quantidade;
    document.getElementById('preco').value = produto.Preco;
    document.getElementById('categoria').value = produto.CategoriaId;
    document.getElementById('titulo-formulario').textContent = 'Editar produto';
    cancelar.style.display = 'block';
}

async function excluirProduto(id) {
    if (!confirm('Deseja excluir este produto?')) return;
    const resposta = await fetch(`/api/produtos/${id}`, {method: 'DELETE'});
    const resultado = await resposta.json();
    mensagem.textContent = resultado.mensagem || resultado.erro;
    carregarProdutos();
}

function limparFormulario() {
    formulario.reset();
    document.getElementById('produto-id').value = '';
    document.getElementById('titulo-formulario').textContent = 'Cadastrar produto';
    cancelar.style.display = 'none';
}

cancelar.addEventListener('click', limparFormulario);
carregarCategorias();
carregarProdutos();

