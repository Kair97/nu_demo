/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

const HOME_XMLID = "custom_home_dashboard.menu_custom_home_dashboard_root";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.homeMenu = useService("home_menu");
        this.hm = useState(this.homeMenu.state);
    },

    /**
     * True when the app grid is on screen -- either because the overlay is
     * toggled open, or because the user's landing page *is* the dashboard.
     * Both cases must hide the navbar chrome, otherwise the landing page shows
     * a stray "Dashboard" title and a generic icon while the toggled overlay
     * shows nothing, which looks inconsistent.
     */
    get showingHomeMenu() {
        return this.hm.hasHomeMenu || this.currentApp?.xmlid === HOME_XMLID;
    },
});
