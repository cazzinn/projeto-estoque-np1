CREATE TABLE IF NOT EXISTS Categorias (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Produtos (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Nome VARCHAR(100) NOT NULL,
    Quantidade INTEGER NOT NULL,
    Preco DECIMAL(10, 2) NOT NULL,
    CategoriaId INTEGER NOT NULL,
    FOREIGN KEY (CategoriaId) REFERENCES Categorias(Id)
);

INSERT OR IGNORE INTO Categorias (Id, Nome) VALUES (1, 'Alimentos');
INSERT OR IGNORE INTO Categorias (Id, Nome) VALUES (2, 'Bebidas');
INSERT OR IGNORE INTO Categorias (Id, Nome) VALUES (3, 'Limpeza');

INSERT OR IGNORE INTO Produtos (Id, Nome, Quantidade, Preco, CategoriaId)
VALUES (1, 'Arroz 5 kg', 10, 28.90, 1);

INSERT OR IGNORE INTO Produtos (Id, Nome, Quantidade, Preco, CategoriaId)
VALUES (2, 'Refrigerante 2 L', 15, 8.50, 2);

