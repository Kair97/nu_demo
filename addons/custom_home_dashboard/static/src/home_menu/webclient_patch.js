/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { WebClient } from "@web/webclient/webclient";
import { useService } from "@web/core/utils/hooks";

/**
 * Landing on a bare "/odoo" should show the home menu, not auto-open whichever
 * app happens to sort first. This also means a refresh while the home menu is
 * open stays on the home menu instead of bouncing into an app.
 */
patch(WebClient.prototype, {
    setup() {
        super.setup();
        this.homeMenu = useService("home_menu");
    },

    _loadDefaultApp() {
        return this.homeMenu.toggle(true);
    },
});
