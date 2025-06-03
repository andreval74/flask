from flask import Flask, request, jsonify
from flask_cors import CORS
import solcx

app = Flask(__name__)
CORS(app)

# Instalar e configurar o compilador Solidity
solcx.install_solc('0.8.21')
solcx.set_solc_version('0.8.21')

@app.route('/compile', methods=['POST'])
def compile_contract():
    data = request.get_json()
    source_code = data.get('source')
    if not source_code:
        return jsonify({'error': 'Código-fonte ausente.'}), 400

    try:
        compiled = solcx.compile_source(
            source_code,
            output_values=["abi", "bin"]
        )
        contract_id, contract_interface = next(iter(compiled.items()))
        return jsonify({
            'abi': contract_interface['abi'],
            'bytecode': contract_interface['bin']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)