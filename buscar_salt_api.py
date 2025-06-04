from flask import Flask, request, jsonify
from flask_cors import CORS
from eth_utils import keccak, to_checksum_address
import time
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.route('/buscar-salt', methods=['OPTIONS'])
def options_salt():
    return '', 200

def get_create2_address(factory, salt, bytecode_hash):
    parts = [b'\xff', bytes.fromhex(factory[2:]), bytes.fromhex(salt[2:]), bytes.fromhex(bytecode_hash[2:])]
    addr = keccak(b''.join(parts))[-20:]
    return to_checksum_address('0x' + addr.hex())

@app.route('/buscar-salt', methods=['POST'])
def buscar_salt():
    data = request.get_json()
    bytecode = data.get('bytecode')
    final = data.get('final', '').lower().replace('0x', '')
    factory = data.get('factory')
    max_attempts = int(data.get('max', 10000000))

    if not bytecode or not final or not factory:
        return jsonify({"erro": "Campos obrigatórios ausentes."}), 400

    hash_bytecode = keccak(bytes.fromhex(bytecode[2:])).hex()
    inicio = time.time()

    for i in range(max_attempts):
        salt = hex(i)[2:].rjust(64, '0')
        full_salt = '0x' + salt
        endereco = get_create2_address(factory, full_salt, '0x' + hash_bytecode)
        if endereco.lower().endswith(final):
            return jsonify({
                "salt": full_salt,
                "endereco": endereco,
                "tentativas": i,
                "tempo": round(time.time() - inicio, 2)
            })

    return jsonify({"erro": "Nenhum salt encontrado após {} tentativas.".format(max_attempts)}), 404

# Importante para o Render: usar a porta fornecida pelo sistema
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
