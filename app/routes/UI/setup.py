def get_setup_script():
    return """
        let setupShopData = null;
        let setupUsersData = [];
        let setupShopsData = [];
        let setupIsArchitect = false;
        let setupSelectedShopDomain = '';
        let setupDefaultDomain = '';
        let setupEditMode = false;

        let setupUsersAbort = null;
        let setupShopsAbort = null;
        let setupShopAbort = null;

        function setupEscape(value) {
            return String(value || '')
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/\"/g, '&quot;')
                .replace(/'/g, '&#39;');
        }

        function fetchWithTimeout(url, options = {}, timeout = 10000) {
            const controller = new AbortController();
            const id = setTimeout(() => controller.abort(), timeout);

            return fetch(url, {
                ...options,
                signal: controller.signal
            }).finally(() => clearTimeout(id));
        }

        async function safeFetch(url, options = {}) {
            const resp = await fetchWithTimeout(url, options, 10000);

            if (!resp.ok) {
                throw new Error(`HTTP ${resp.status}`);
            }

            try {
                return await resp.json();
            } catch {
                throw new Error('Invalid JSON response');
            }
        }

        async function setupLoadContext() {
            const pane = document.getElementById('setupShopsPane');
            const addShopBtn = document.getElementById('setupAddShopBtn');

            try {
                const data = await safeFetch('/api/setup/context', { credentials: 'include' });

                setupIsArchitect = !!data.is_architect;
                setupDefaultDomain = String(data.default_domain || '').trim().toLowerCase();

                if (!setupSelectedShopDomain) {
                    setupSelectedShopDomain = setupDefaultDomain;
                }

                if (pane) pane.style.display = setupIsArchitect ? 'block' : 'none';
                if (addShopBtn) addShopBtn.style.display = setupIsArchitect ? 'inline-block' : 'none';

            } catch (error) {
                console.error('Context error:', error);
                setupIsArchitect = false;
                if (pane) pane.style.display = 'none';
                if (addShopBtn) addShopBtn.style.display = 'none';
            }
        }

        function setupBuildScopeQuery() {
            if (!setupIsArchitect || !setupSelectedShopDomain) return '';
            return `?shop_domain=${encodeURIComponent(setupSelectedShopDomain)}`;
        }

        function setupBuildScopePayload() {
            if (!setupIsArchitect || !setupSelectedShopDomain) return {};
            return { shop_domain: setupSelectedShopDomain };
        }

        async function setupLoadData() {
            await setupLoadContext();

            if (setupIsArchitect) {
                await setupLoadShops();
            }

            await setupLoadShop();
            await setupLoadUsers();
        }

        async function setupLoadShops() {
            if (setupShopsAbort) setupShopsAbort.abort();
            setupShopsAbort = new AbortController();

            const wrap = document.getElementById('setupShopsCards');
            if (wrap) wrap.innerHTML = 'Loading shops...';

            try {
                const data = await safeFetch('/api/setup/shops', {
                    credentials: 'include',
                    signal: setupShopsAbort.signal
                });

                setupShopsData = Array.isArray(data.shops) ? data.shops : [];

                if (!setupSelectedShopDomain && setupShopsData.length) {
                    setupSelectedShopDomain = setupShopsData[0].domain;
                }

                setupRenderShops();

            } catch (error) {
                if (error.name === 'AbortError') return;
                console.error(error);
                if (wrap) wrap.innerHTML = 'Error loading shops. <button onclick="setupLoadShops()">Retry</button>';
            }
        }

        async function setupLoadShop() {
            if (setupShopAbort) setupShopAbort.abort();
            setupShopAbort = new AbortController();

            try {
                const data = await safeFetch(`/api/setup/shop${setupBuildScopeQuery()}`, {
                    credentials: 'include',
                    signal: setupShopAbort.signal
                });

                setupShopData = data.shop || {};
                setupRenderShopDisplay();

            } catch (error) {
                if (error.name === 'AbortError') return;
                console.error('Shop error:', error);
            }
        }

        async function setupLoadUsers() {
            if (setupUsersAbort) setupUsersAbort.abort();
            setupUsersAbort = new AbortController();

            const body = document.getElementById('setupUsersBody');
            if (body) body.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';

            try {
                const data = await safeFetch(`/api/setup/users${setupBuildScopeQuery()}`, {
                    credentials: 'include',
                    signal: setupUsersAbort.signal
                });

                setupUsersData = Array.isArray(data.users) ? data.users : [];

                setupRenderUsers();

            } catch (error) {
                if (error.name === 'AbortError') return;
                console.error(error);

                if (body) {
                    body.innerHTML = `
                        <tr>
                            <td colspan="5">
                                Error loading users.
                                <br/>
                                <button onclick="setupLoadUsers()">Retry</button>
                            </td>
                        </tr>
                    `;
                }
            }
        }

        function setupRenderShops() {
            const wrap = document.getElementById('setupShopsCards');
            if (!wrap) return;

            if (!setupShopsData.length) {
                wrap.innerHTML = 'No shops found.';
                return;
            }

            wrap.innerHTML = setupShopsData.map(shop => {
                const domain = setupEscape(shop.domain || '');
                const name = setupEscape(shop.shop_name || domain);

                return `
                    <div class="shop-card" data-domain="${domain}" style="padding:10px; border:1px solid #ddd; margin-bottom:6px; cursor:pointer;">
                        <strong>${name}</strong>
                    </div>
                `;
            }).join('');
        }

        document.addEventListener('click', (e) => {
            const card = e.target.closest('.shop-card');
            if (card) {
                setupSelectedShopDomain = card.dataset.domain;
                setupLoadShop();
                setupLoadUsers();
            }
        });
    """