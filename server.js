const express = require('express');
const cors = require('cors');
const { ethers } = require('ethers');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware CORS liberando apenas seu domínio
app.use(cors({
  origin: 'https://webkeeper.com.br',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type']
}));

app.use(express.json());

app.post('/buscar_salt', async (req, res) => {
  const { factoryAddress, bytecode, desiredEnding } = req.body;

  if (!factoryAddress || !bytecode || !desiredEnding) {
    return res.status(400).json({ erro: 'Parâmetros ausentes' });
  }

  const cleanBytecode = bytecode.startsWith('0x') ? bytecode : '0x' + bytecode;
  const bytecodeHash = ethers.utils.keccak256(cleanBytecode);

  const endMin = desiredEnding.toLowerCase().replace(/^0x/, '');

  let salt;
  let foundAddress;
  const maxTries = 100000000;

  for (let i = 0; i < maxTries; i++) {
    const saltHex = ethers.utils.hexZeroPad(ethers.utils.hexlify(i), 32);
    const address = ethers.utils.getCreate2Address(factoryAddress, saltHex, bytecodeHash);

    if (address.toLowerCase().endsWith(endMin)) {
      salt = saltHex;
      foundAddress = address;
      break;
    }

    // Opcional: log a cada milhão
    if (i % 1000000 === 0) console.log(`Tentativas: ${i}`);
  }

  if (salt && foundAddress) {
    return res.json({
      salt,
      address: foundAddress
    });
  } else {
    return res.status(404).json({ erro: 'Endereço não encontrado' });
  }
});

app.listen(PORT, () => {
  console.log(`🚀 API rodando na porta ${PORT}`);
});
          
