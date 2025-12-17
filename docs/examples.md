# Output examples

## Test container

With pretty json:

```bash
uv run contest --json --pretty test-container ubuntu
```

```json
{
  "id": "12345",
  "name": "container_test_ubuntu_latest_1765840163",
  "command": ["echo", "Container", "is", "running"],
  "stdout": "Container is running",
  "stderr": ""
}
```

With pretty:

```bash
uv run contest --pretty test-container ubuntu
```

<div
  style="font-family:Menlo,'DejaVu Sans Mono',Consolas,'Courier New',monospace;
         font-size:13px;
         line-height:1.45;
         max-width:980px;
         color:inherit"
>
  <div
    style="font-weight:700;
           margin:0 0 8px 0;
           text-align:center"
  >
    container
  </div>
  <table
    style="width:100%;
           border-collapse:collapse;
           border:1px solid currentColor"
  >
    <thead>
      <tr>
        <th
          style="text-align:left;
                 padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 font-weight:700"
        >
          key
        </th>
        <th
          style="text-align:left;
                 padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 font-weight:700"
        >
          value
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">id</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top;
                 word-break:break-all"
        >
          <span style="color:#c792ea">
            af2557638d7aca686f94a4a8a221ded38fc4d2baa1bbd3fbc179afb75b31ffcd
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">name</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">
            container_test_ubuntu_latest_1765839880
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">command</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">
            ['echo', 'Container', 'is', 'running']
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">stdout</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">Hello, world</span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">stderr</span>
        </td>
        <td style="padding:8px 10px;vertical-align:top">
          <span style="color:#c792ea"></span>
        </td>
      </tr>
    </tbody>
  </table>
</div>

## Test config

With pretty json:

```bash
uv run contest --json --pretty test-config
```

```json
[
  {
    "id": "12345",
    "name": "container_test_alpine_latest_1765840328",
    "command": ["echo", "Hello,", "world"],
    "stdout": "Hello, world",
    "stderr": ""
  },
  {
    "id": "12346",
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

<div
  style="font-family:Menlo,'DejaVu Sans Mono',Consolas,'Courier New',monospace;
         font-size:13px;
         line-height:1.45;
         max-width:980px;
         color:inherit"
>
  <div
    style="font-weight:700;
           margin:0 0 8px 0;
           text-align:center"
  >
    container
  </div>
  <table
    style="width:100%;
           border-collapse:collapse;
           border:1px solid currentColor"
  >
    <thead>
      <tr>
        <th
          style="text-align:left;
                 padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 font-weight:700"
        >
          key
        </th>
        <th
          style="text-align:left;
                 padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 font-weight:700"
        >
          value
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">id</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top;
                 word-break:break-all"
        >
          <span style="color:#c792ea">
            10a3310ae05dad5ddd9c6cfedba1313929f1f924e0ad1c7b1597ca504b80c46b
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">name</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">
            container_test_alpine_latest_1765840443
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">command</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">
            ['echo', 'Hello,', 'world']
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">stdout</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">Hello, world</span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">stderr</span>
        </td>
        <td style="padding:8px 10px;vertical-align:top">
          <span style="color:#c792ea"></span>
        </td>
      </tr>
    </tbody>
  </table>

  <div
    style="font-weight:700;
           margin:0 0 8px 0;
           text-align:center"
  >
    container
  </div>
  <table
    style="width:100%;
           border-collapse:collapse;
           border:1px solid currentColor"
  >
    <thead>
      <tr>
        <th
          style="text-align:left;
                 padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 font-weight:700"
        >
          key
        </th>
        <th
          style="text-align:left;
                 padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 font-weight:700"
        >
          value
        </th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">id</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top;
                 word-break:break-all"
        >
          <span style="color:#c792ea">
            67fd34157c99f7037c2acf68b9af3c9272bb184bc83b8b6d26730cd9cc87e950
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">name</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">
            container_test_ubuntu_latest_1765840570
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">command</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">
            ['echo', 'Hello,', 'world']
          </span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">stdout</span>
        </td>
        <td
          style="padding:8px 10px;
                 border-bottom:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#c792ea">Hello, world</span>
        </td>
      </tr>
      <tr>
        <td
          style="padding:8px 10px;
                 border-right:1px solid currentColor;
                 vertical-align:top"
        >
          <span style="color:#2aa198">stderr</span>
        </td>
        <td style="padding:8px 10px;vertical-align:top">
          <span style="color:#c792ea"></span>
        </td>
      </tr>
    </tbody>
  </table>
</div>
