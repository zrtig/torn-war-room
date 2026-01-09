# 🛡️ War-Room Console

War-Room Console is a specialized management utility designed for Torn City faction leadership. It streamlines the complex process of calculating ranked war payouts by utilizing a dual-weighted system that balances raw hit volume with respect impact.


<p align="center">
  <img src="https://i.imgur.com/s1Gru34.png" width="600" alt="War-Room Console">
</p>

## Overview

The console provides a centralized "Situation Room" interface to handle post-war finances. By connecting directly to the Torn API, it eliminates manual data entry and ensures that every member is compensated fairly based on faction-defined performance metrics.

## Features

* **Automated Intelligence:** Automatically fetches the latest Ranked War ID and Faction ID based on the provided API key.
* **Biased Weighting System:** A proprietary slider system allowing leadership to decide the importance of Hit Volume versus Respect Impact.
* **Operational Tax Management:** Integrated slider to deduct faction cuts for armory maintenance or cache refills before calculating member shares.
* **Tactical Manifest View:** A high-visibility, monospace data display for reviewing operative performance and final payout amounts.
* **CSV Export:** Generate professional manifests for record-keeping or mass-payout processing.

## Calculation Logic

The tool calculates payouts using a weighted distribution model:

1. **Volume Share:** (Member Hits / Total Faction Hits) * Volume Weight
2. **Impact Share:** (Member Respect / Total Faction Respect) * Impact Weight
3. **Total Share:** Volume Share + Impact Share
4. **Final Payout:** Total Share * (Total Bounty - Operational Tax)

This ensures that "wall-fillers" (high volume) and "heavy hitters" (high respect) are both incentivized according to the specific needs of the faction's strategy.

## Installation

1. Ensure Python 3.x is installed on your system.
2. Install the required dependencies:
```bash
pip install customtkinter requests

```


3. Run the application:
```bash
python war_room_console.py

```



## Configuration

* **API Key:** Requires a key with basic faction access. The key can be saved locally for faster deployment in future sessions.
* **Intel Fetch:** Uses the 'rankedwars' selection to find the most recent conflict.
* **Exporting:** Data is saved in a standard .csv format compatible with Excel and Google Sheets.

## Disclaimer

This tool is a third-party utility and is not officially affiliated with Torn City or Chedburn. Ensure your API key is kept secure; the 'Save Key' feature stores your key in a local JSON file within the application directory.

---

Developed by car [3581510]
