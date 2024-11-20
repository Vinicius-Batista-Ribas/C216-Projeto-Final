DROP TABLE IF EXISTS "mods";

CREATE TABLE "mods" (
    "id" SERIAL PRIMARY KEY,
    "nome" VARCHAR(255) NOT NULL,
    "jogo" VARCHAR(255) NOT NULL,
    "descricao" VARCHAR(255) NOT NULL,
    "versao" VARCHAR(255) NOT NULL,
    "autores" VARCHAR(255) NOT NULL,
    "categoria" VARCHAR(255) NOT NULL,
    "tamanho" VARCHAR(255) NOT NULL
);

INSERT INTO "mods" ("nome", "jogo", "descricao", "versao", "autores", "categoria", "tamanho") 
VALUES 
    ('escudo do capitao america', 'BG3', 'Adiciona um escudo lendario exclusivo, completo com um modelo personalizado e novas passivas e magias', '2.32', 'irineu', 'Armaduras e escudos', '15.2MB'),
    ('move it!', 'Cities: Skylines', 'Permite que voce mova as construcoes livremente no mapa', '2.32', 'irineu', 'Personalizacao', '15.2MB'),
    ('Muito mais monstros', 'Genshin Impact', 'Adiciona mais monstros em lugares aleatorios do mapa', '2.32', 'irineu', 'Monstros', '15.2MB');
