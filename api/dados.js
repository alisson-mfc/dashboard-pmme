// api/dados.js - Serverless Function para servir dados de forma segura
export default function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Content-Type', 'application/json');

  // Suporte a OPTIONS para CORS preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    // Ler dados da variável de ambiente
    const dados = process.env.DADOS_JSON;

    if (!dados) {
      console.error('DADOS_JSON não configurado nas variáveis de ambiente');
      return res.status(500).json({
        error: 'Dados não disponíveis',
        message: 'Configure a variável de ambiente DADOS_JSON'
      });
    }

    // Parse e retornar JSON
    const dadosObj = JSON.parse(dados);
    res.status(200).json(dadosObj);

  } catch (error) {
    console.error('Erro ao processar dados:', error.message);
    res.status(500).json({
      error: 'Erro ao carregar dados',
      message: error.message
    });
  }
}
