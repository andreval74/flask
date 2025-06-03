from flask import Flask, request, jsonify
from flask_cors import CORS
import solcx
from eth_utils import keccak  # Novo import para calcular o hash

app = Flask(__name__)
CORS(app)

# Instala e configura o compilador Solidity
solcx.install_solc('0.8.21')
solcx.set_solc_version('0.8.21')

@app.route('/compile', methods=['POST'])
def compile_contract():
    data = request.get_json()
    source_code = data.get('source') or data.get('code')
    if not source_code:
        return jsonify({'error': 'Código-fonte ausente.'}), 400

    try:
        compiled = solcx.compile_source(
            source_code,
            output_values=["abi", "bin"]
        )
        contract_id, contract_interface = next(iter(compiled.items()))
        bytecode = contract_interface['bin']
        hash_hex = '0x' + keccak(bytes.fromhex(bytecode)).hex()  # Gera o hash do bytecode

        return jsonify({
            'abi': contract_interface['abi'],
            'bytecode': bytecode,
            'hash': hash_hex  # Incluído no JSON de resposta
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
