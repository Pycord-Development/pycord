include .env
export PYCORD_TEST_MODE
export PYCORD_BOT_TOKEN
export PYCORD_CERT_PATH

export PYTHONWARNINGS=ignore # Ignore useless proxy.py warnings

CA_KEYFILE := pycord-key.pem
CA_CERTFILE := pycord-cert.pem
CA_SIGNKEY := pycord-signkey.pem

envecho:
	@echo $(PYCORD_TEST_MODE)
	@echo $(PYCORD_BOT_TOKEN)
	@echo $(PYCORD_CERT_PATH)

runtests:
	python -m unittest

gencerts:
	# Create CA keyfile and remove passphrase
	python -m proxy.common.pki gen_private_key \
		--private-key-path $(CA_KEYFILE)
	python -m proxy.common.pki remove_passphrase \
		--private-key-path $(CA_KEYFILE)

	# Create a CA certificate
	python -m proxy.common.pki gen_public_key \
		--private-key-path $(CA_KEYFILE) \
		--public-key-path $(CA_CERTFILE)

	# Create CA signing key and remove passphrase
	python -m proxy.common.pki gen_private_key \
		--private-key-path $(CA_SIGNKEY)
	python -m proxy.common.pki remove_passphrase \
		--private-key-path $(CA_SIGNKEY)
