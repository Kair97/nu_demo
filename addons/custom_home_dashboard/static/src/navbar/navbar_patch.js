/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.homeMenu = useService("home_menu");
        this.hm = useState(this.homeMenu);
    },

    /**
     * The home menu is a real action now, so this is simply whether it is the
     * one currently mounted -- no need to also special-case a landing action.
     */
    get showingHomeMenu() {
        return this.hm.hasHomeMenu;
    },
});
