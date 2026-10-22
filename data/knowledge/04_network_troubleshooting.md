# Dialog Care Copilot — Network & Device Troubleshooting (SAMPLE DATA)

> **Training data only.** Invented for the hONE × Dialog Foundry workshop.

## Before troubleshooting: check for outages

Always check for a **known network outage** in the customer's district before
running device troubleshooting steps. If there is an active outage, tell the
customer the estimated restoration time and do **not** raise a new fault ticket
(the outage ticket already covers them).

## Mobile data not working (4G/5G)

1. Confirm the customer has an active data package or balance.
2. Toggle flight mode on for 10 seconds, then off.
3. Check that the APN is `dialogbb` (Android: Settings → Mobile network → Access Point Names).
4. Make sure the preferred network type is set to **5G/4G/3G auto**.
5. Restart the handset.
6. If it is still not working, raise a ticket with category `MOBILE_DATA` and
   include the handset model and district.

## Slow speeds

- Speeds can drop in crowded locations (events, Pettah market, Galle Face on
  weekends) and during heavy rain.
- Run a speed test in the MyCare app. If download speed is below 2 Mbps on 4G
  for more than 24 hours at the same location, raise a `COVERAGE` ticket with the
  GPS location.

## Home Broadband (Fibre and 4G Home)

- **Fibre (FTTH)**: check that the ONT's `PON` light is solid green. A red `LOS`
  light means a fibre cut: raise a `FIBRE_FAULT` ticket. Technician visits are
  scheduled within 24 hours in Colombo, Gampaha and Kalutara districts, and
  within 48 hours elsewhere.
- **4G Home router**: place the router near a window, away from metal objects.
  Restart it by holding the power button for 5 seconds.

## VoLTE and Wi-Fi Calling

- VoLTE is supported on most handsets released after 2019. Enable it in
  Settings → Mobile network → VoLTE calls.
- Wi-Fi Calling works over any Wi-Fi connection in Sri Lanka. Calls are charged
  at local rates.

## eSIM

- An eSIM can be issued at any Care Centre or through the MyCare app after NIC
  verification with a selfie (eKYC).
- An eSIM can only be installed **once** per QR code. If the customer deletes it,
  a new QR must be issued (fee: LKR 200).

## SIM replacement

- Lost or damaged SIM: visit a Care Centre with the original **NIC** or passport.
  Fee: LKR 150. The SIM is replaced on the spot.
- For security, SIM replacement can **never** be done over chat or phone.
