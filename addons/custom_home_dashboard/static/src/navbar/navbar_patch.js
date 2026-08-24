/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";
import { useService } from "@web/core/utils/hooks";
import { useState } from "@odoo/owl";

patch(NavBar.prototype, {
    setup() {
        super.setup();
        this.homeMenu = useService("home_menu");
        this.hm = useState(this.homeMenu.state);
        this.toggleHover = useState({ value: false });
    },
});
