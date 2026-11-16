document.addEventListener('DOMContentLoaded', () => {
  const inputArquivo = document.getElementById('arquivo');
  const nomeArquivo = document.getElementById('nomeArquivo');
  const botaoIniciar = document.getElementById('iniciar');
  const statusDiv = document.getElementById('status');
  const btnSelecionarTudo = document.getElementById('selecionarTudo');
  const botaoAbrirArquivo = document.getElementById('botaoAbrirArquivo');

  let arquivoSelecionado = null;

  inputArquivo.addEventListener('change', () => {
    if (inputArquivo.files.length > 0) {
      arquivoSelecionado = inputArquivo.files[0];
      nomeArquivo.textContent = arquivoSelecionado.name;
    } else {
      nomeArquivo.textContent = "AQUI FICARÁ O NOME DO ARQUIVO";
    }
  });

  botaoAbrirArquivo.addEventListener('click', () => {
    inputArquivo.click();  // usa o <input type="file"> tradicional
  });



  // Receber caminho e atualizar visual
  window.electronAPIReceber && window.electronAPIReceber((caminho) => {
    const nome = caminho.split('\\').pop();
    nomeArquivo.textContent = nome;

    // Cria um objeto File do caminho (apenas se for usar File com input ou FormData diretamente)
    // Como workaround, podemos reenviar via Electron → backend no futuro
  });


  let tudoSelecionado = false;

  btnSelecionarTudo.addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('.opcao-mineracao');

    tudoSelecionado = !tudoSelecionado;

    checkboxes.forEach(checkbox => {
      checkbox.checked = tudoSelecionado;
    });

    // Atualiza o texto do botão dinamicamente
    btnSelecionarTudo.textContent = tudoSelecionado ? 'Limpar seleção' : 'Selecionar tudo';
  });


  botaoIniciar.addEventListener('click', () => {
    if (!arquivoSelecionado) {
      alert("⚠️ Por favor, selecione um arquivo CSV.");
      return;
    }

    const opcoesSelecionadas = Array.from(document.querySelectorAll('.opcao-mineracao:checked')).map(cb => cb.value);

    if (opcoesSelecionadas.length === 0) {
      alert("⚠️ Por favor, selecione ao menos uma opção de mineração.");
      return;
    }

    const formData = new FormData();
    formData.append('arquivo', arquivoSelecionado);
    formData.append('tipos', JSON.stringify(opcoesSelecionadas));

    statusDiv.innerText = "⏳ Processando...";

    fetch('/minerar', {
      method: 'POST',
      body: formData
    })
      .then(res => res.json())
      .then(data => {
        if (data.sucesso) {
          statusDiv.innerText = "✅ Mineração concluída!";
        } else {
          statusDiv.innerText = `❌ Erro: ${data.erro || "Falha desconhecida"}`;
          console.error("Erro na mineração:", data.erro);
        }
      })
      .catch(err => {
        console.error("Erro:", err);
        statusDiv.innerText = "❌ Erro ao enviar dados.";
      });
  });
});
