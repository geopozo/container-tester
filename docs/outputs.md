# Output examples

## Test container

```bash
uv run contest --json --pretty test-container ubuntu --command "echo Hello, world"
```

With pretty json:

```json
{
  "id": "8ccd21a13fd4dd9bb7a4785305aa130ba705484efe4652bbeae5afc7a22d3326",
  "name": "container_test_ubuntu_latest_1765840163",
  "command": ["echo", "Hello,", "world"],
  "stdout": "Hello, world",
  "stderr": ""
}
```

With pretty:

```bash
uv run contest --pretty test-container ubuntu --command "echo Hello, world"
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><code style="font-family:inherit"><span style="font-style: italic">                                  container                                   </span>
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> key     </span>┃<span style="font-weight: bold"> value                                                            </span>┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│<span style="color: #008080; text-decoration-color: #008080"> id      </span>│<span style="color: #800080; text-decoration-color: #800080"> af2557638d7aca686f94a4a8a221ded38fc4d2baa1bbd3fbc179afb75b31ffcd </span>│
│<span style="color: #008080; text-decoration-color: #008080"> name    </span>│<span style="color: #800080; text-decoration-color: #800080"> container_test_ubuntu_latest_1765839880                          </span>│
│<span style="color: #008080; text-decoration-color: #008080"> command </span>│<span style="color: #800080; text-decoration-color: #800080"> [&#x27;echo&#x27;, &#x27;Hello,&#x27;, &#x27;world&#x27;]                                      </span>│
│<span style="color: #008080; text-decoration-color: #008080"> stdout  </span>│<span style="color: #800080; text-decoration-color: #800080"> Hello, world                                                     </span>│
│<span style="color: #008080; text-decoration-color: #008080"> stderr  </span>│<span style="color: #800080; text-decoration-color: #800080">                                                                  </span>│
└─────────┴──────────────────────────────────────────────────────────────────┘
</code></pre>

## Test config

With pretty json:

```bash
uv run contest --json --pretty test-config
```

```json
[
  {
    "id": "1b17ae475cf05af69dca70e930f7c90c2ac5cb57a0af972a36e7e535ecee947b",
    "name": "container_test_alpine_latest_1765840328",
    "command": ["echo", "Hello,", "world"],
    "stdout": "Hello, world",
    "stderr": ""
  },
  {
    "id": "f98ed41100035f349f9897fa2ce3a14f8dee4433cc0b79b8ea09841fde216fd7",
    "name": "container_test_ubuntu_latest_1765840603",
    "command": ["echo", "Hello,", "world"],
    "stdout": "Hello, world",
    "stderr": ""
  }
]
```

With pretty:

```bash
uv run contest --pretty test-config
```

<pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><code style="font-family:inherit"><span style="font-style: italic">                                  container                                   </span>
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> key     </span>┃<span style="font-weight: bold"> value                                                            </span>┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│<span style="color: #008080; text-decoration-color: #008080"> id      </span>│<span style="color: #800080; text-decoration-color: #800080"> 10a3310ae05dad5ddd9c6cfedba1313929f1f924e0ad1c7b1597ca504b80c46b </span>│
│<span style="color: #008080; text-decoration-color: #008080"> name    </span>│<span style="color: #800080; text-decoration-color: #800080"> container_test_alpine_latest_1765840443                          </span>│
│<span style="color: #008080; text-decoration-color: #008080"> command </span>│<span style="color: #800080; text-decoration-color: #800080"> [&#x27;echo&#x27;, &#x27;Hello,&#x27;, &#x27;world&#x27;]                                      </span>│
│<span style="color: #008080; text-decoration-color: #008080"> stdout  </span>│<span style="color: #800080; text-decoration-color: #800080"> Hello, world                                                     </span>│
│<span style="color: #008080; text-decoration-color: #008080"> stderr  </span>│<span style="color: #800080; text-decoration-color: #800080">                                                                  </span>│
└─────────┴──────────────────────────────────────────────────────────────────┘
</code>
<code style="font-family:inherit"><span style="font-style: italic">                                  container                                   </span>
┏━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃<span style="font-weight: bold"> key     </span>┃<span style="font-weight: bold"> value                                                            </span>┃
┡━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│<span style="color: #008080; text-decoration-color: #008080"> id      </span>│<span style="color: #800080; text-decoration-color: #800080"> 67fd34157c99f7037c2acf68b9af3c9272bb184bc83b8b6d26730cd9cc87e950 </span>│
│<span style="color: #008080; text-decoration-color: #008080"> name    </span>│<span style="color: #800080; text-decoration-color: #800080"> container_test_ubuntu_latest_1765840570                          </span>│
│<span style="color: #008080; text-decoration-color: #008080"> command </span>│<span style="color: #800080; text-decoration-color: #800080"> [&#x27;echo&#x27;, &#x27;Hello,&#x27;, &#x27;world&#x27;]                                      </span>│
│<span style="color: #008080; text-decoration-color: #008080"> stdout  </span>│<span style="color: #800080; text-decoration-color: #800080"> Hello, world                                                     </span>│
│<span style="color: #008080; text-decoration-color: #008080"> stderr  </span>│<span style="color: #800080; text-decoration-color: #800080">                                                                  </span>│
└─────────┴──────────────────────────────────────────────────────────────────┘
</code></pre>
