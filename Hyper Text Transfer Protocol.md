HTTP is one of the most widely used communication protocol on the internet. Some of its most notable characteristics are:
- **Unidirectional connection**: A connection can only be initiated from a client to a server
- **Stateless protocol**: Each connection is independent and the connection closes once the communication is complete
- **connection categories**: Persistent (not close after the end of a transaction like a DB connection) and non-persistent
- **plain text transmission**: High transmission efficiency. The data is sent in a form that **anyone who intercepts it can read directly** — no protection. Reason for HTTPS.

# HTTP Message Structure

An HTTP request consists of three parts:
- **Start line**
	request: `<Method> <URL> <Version>`
	response: `<Version> <StatusCode> <ReasonPhrase>`
- **Header fields**:
	`<FieldName>:<Value>`
	`<FieldName>:<Value>`
	...
- **Body**: Can contain arbitrary data (photo, video, text, ...)

# HTTP Request Methods

- **GET**: requests resources from the server
- **POST**: sends data to the server
- **PUT**: writes a document to the server (in a specific location)
- **DELETE**: deletes the resource specified in the URL
- **HEAD**: returns only the headers associated with a resource, but not the body
- **TRACE**: if a request initiated by a client passes through an application such as a firewall or agent, the original HTTP request is modified. TRACE enables the client to view the exact request sent to the server
- **OPTIONS**: requests permitted communication options

# HTTPS

- Prevents security risks caused by HTTP plain text transmission.
- Requires certificates from the CA.
- Works on TCP-based SSL/TLS to encrypt all contents.
- Runs on port 443 by default, which is different from HTTP.
- Has encryption/decryption overhead that slows access speed, but this impact is negligible with optimization.
- Currently, almost all websites use HTTPS.

# HTTPS Session Process

- The client sends available encryption methods and requests a certificate from the server.
- The server returns the certificate and the selected encryption method to the client.
- The client obtains and verifies the certificate in terms of:
	- Legitimacy of the source
	- Validity of content
	- Valid of the certificate
	- Whether the name of the owner is the same as that of the target host
- The client generates a temporary session key (symmetric key), encrypts the data using the public key of the server, and sends the encrypted data to the server to complete key exchange.
- The server uses this key to encrypt the requested resource and sends a response to the client.

# Cookies and Sessions

# HTTP Response Codes

- 
