import sys
import cbor
import json
import sawtooth_sdk
import urllib.request

from hashlib import sha512
from urllib.error import HTTPError
from sawtooth_signing import CryptoFactory
from sawtooth_signing import create_context
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

#create a random private to test a transaction
context = create_context('secp256k1')
private_key = context.new_random_private_key()
signer = CryptoFactory(context).new_signer(private_key)


#encode payload
#simple payload, name and owner
payload = {
    'action' : 'create',
    'asset' : 'test',
    'owner' : 'test1' }

payload_bytes = cbor.dumps(payload)

#create transaction headers
txn_header_bytes = TransactionHeader(
    family_name='code-smell',
    family_version='0.1',
    inputs=['19d832'],
    outputs=['19d832'],
    signer_public_key=signer.get_public_key().as_hex(),
    # In this example, we're signing the batch with the same private key,
    # but the batch can be signed by another party, in which case, the
    # public key will need to be associated with that key.
    batcher_public_key=signer.get_public_key().as_hex(),
    # In this example, there are no dependencies.  This list should include
    # an previous transaction header signatures that must be applied for
    # this transaction to successfully commit.
    # For example,
    # dependencies=['540a6803971d1880ec73a96cb97815a95d374cbad5d865925e5aa0432fcf1931539afe10310c122c5eaae15df61236079abbf4f258889359c4d175516934484a'],
    dependencies=[],
    payload_sha512=sha512(payload_bytes).hexdigest()
).SerializeToString()

#create transaction
signature = signer.sign(txn_header_bytes)

txn = Transaction(
    header=txn_header_bytes,
    header_signature=signature,
    payload=payload_bytes
)

#create batch headers
txns = [txn]
batch_header_bytes = BatchHeader(
    signer_public_key=signer.get_public_key().as_hex(),
    transaction_ids=[txn.header_signature for txn in txns],
).SerializeToString()

#create the batch
signature = signer.sign(batch_header_bytes)
batch = Batch(
    header=batch_header_bytes,
    header_signature=signature,
    transactions=txns
)

#encode batch in a batchList
batch_list_bytes = BatchList(batches=[batch]).SerializeToString()

#send batch to validator
try:
    request = urllib.request.Request(
        'http://127.0.0.1:8008/batches',
        batch_list_bytes,
        method='POST',
        headers={'Content-Type': 'application/octet-stream'})
    response = urllib.request.urlopen(request)
    print(response)
except HTTPError as e:
    response = e.file
    print(response)
