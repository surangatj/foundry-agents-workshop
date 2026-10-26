# Prerequisites — Microsoft Foundry Agents Workshop

**Dialog Axiata × Microsoft Foundry · delivered by hONE**
**Monday 26 October 2026 · 09:00–13:30 (Sri Lanka time) · Microsoft office, Colombo + online**

Please complete these **before Monday morning**. Everything else (Python packages,
Azure CLI, code) is pre-installed in the workshop's GitHub Codespace.

**No local administrator access or Azure CLI?** Use the API key supplied by the
facilitators. Set `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL`, `PARTICIPANT_ALIAS`
and `FOUNDRY_API_KEY` in `.env`, then run `python -m labs.lab00_check_setup`.
No Azure CLI installation or `az login` is needed in API-key mode. The resource
must allow API-key authentication for the operations used by the labs.

## 1. Access to a Microsoft Foundry project with a model

You need **one** of the following:

- a shared project endpoint, model deployment name and resource API key supplied
  by the facilitators (no personal Azure sign-in required), **or**
- access to an existing Foundry project that already has a chat model deployed
  (recommended: `gpt-5.4-mini`, or `gpt-5-mini` / `gpt-4.1-mini`), **or**
- permission to deploy a model yourself in a Foundry project.

For API-key access, use the endpoint, deployment name and key from the facilitators
and validate them with Lab 0. Keep the key in `.env`; never commit or share that file.

For personal Azure sign-in, check it now:

1. Open <https://ai.azure.com> and sign in with your Dialog account.
2. Open your project. On **Overview**, copy the **Project endpoint**
   (`https://<resource>.services.ai.azure.com/api/projects/<project>`).
3. Open **Models** (or **Build → Models**) and note the **deployment name** of a chat model.
   If there is none, deploy `gpt-5.4-mini` (Global Standard).
   The workshop's Foundry resources use the **Southeast Asia** Azure region.
4. Open the **Playground**, type "Ayubowan!", and confirm you get a reply.

For personal Azure sign-in, you need at least the **Foundry User** role (formerly *Azure AI User*) on the project.
If step 4 fails, ask your Azure admin for that role.

> Keep the **project endpoint** and **deployment name** handy — you will paste them into Lab 0.

## 2. A GitHub account

- Sign in at <https://github.com> (a personal account is fine).
- GitHub Codespaces is free for personal accounts (60 core-hours/month — the
  workshop uses about 10).

## 3. A laptop with a modern browser

- Chrome or Edge. Nothing needs to be installed locally.
- **Optional (local alternative to Codespaces):** VS Code, Python 3.13, Git and
  the Azure CLI only if using personal Azure sign-in. API-key users do not need the CLI.

## 4. Test sign-in from a Codespace (5 minutes — important!)

**API-key users:** skip device-code sign-in. Copy `.env.example` to `.env`, fill
in the four values above and run Lab 0. Use Codespaces if installing Python
packages on your work laptop is restricted.

**Personal Azure sign-in users:**

Dialog's sign-in policies can block the device-code login that Codespaces uses.
Please test it before Monday:

1. Open the workshop repository and click **Code → Codespaces → Create codespace on main**.
2. When the terminal opens, run:
   ```bash
   az login --use-device-code
   ```
3. Open the link shown, enter the code, and sign in with your Dialog account.
4. Run `az account show`. If you see your account, you're done.

If step 3 is blocked ("your sign-in was blocked" or a conditional-access message),
reply to the invite email so we can arrange a fallback before the session.

## 5. Nice to have (makes the advanced labs work end to end)

These enable specific labs. If they're missing, the facilitators will demo those
parts instead.

| Feature | Used in | What's needed in the Foundry project |
|---|---|---|
| Application Insights connected | Lab 5 (tracing) | Project → Tracing → connect an App Insights resource |
| Azure AI Search connected | Lab 2 Part B (Foundry IQ) | A Search service (Basic or higher) connected to the project |
| Fine-tuning quota | Lab 7 (distillation) | Permission to fine-tune `gpt-4.1-mini` (Global Training) |

## Online participants

Join the Teams meeting from the invite. Questions during the labs go to the
workshop Teams chat; Damika and Rusiru will answer there as well as in the room.
