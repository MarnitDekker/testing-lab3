from playwright.sync_api import expect


class ShopPages:
    def __init__(self, page):
        self.page = page

    def register(self, email, password):
        self.page.goto("/signup")
        self.page.get_by_placeholder("Name").fill("Lab User")
        self.page.get_by_placeholder("Email").fill(email)
        self.page.get_by_placeholder("Password").fill(password)
        self.page.get_by_role("button", name="Sign Up").click()
        expect(self.page).to_have_url("/login")

    def login(self, email, password):
        self.page.goto("/login")
        self.page.locator('input[type="email"]').fill(email)
        self.page.locator('input[type="password"]').fill(password)
        self.page.get_by_role("button", name="Login", exact=True).click()
        expect(self.page).to_have_url("/")

    def search(self, query):
        self.page.goto("/products")
        self.page.get_by_role("searchbox", name="Search products").fill(query)

    def add_tee(self):
        self.search("tee")
        expect(self.page.get_by_role("heading", name="Canvas Cap")).to_have_count(0)
        self.page.get_by_role("button", name="Add Cart").click()
        expect(self.page.get_by_text("Item added to cart")).to_be_visible()
        nav = self.page.get_by_role("navigation")
        nav.get_by_role("link", name="Cart", exact=True).click()
        expect(self.page.get_by_role("heading", name="Your Cart")).to_be_visible()

    def order(self, email):
        self.page.get_by_role("button", name="Proceed to Checkout").click()
        for field, value in {
            "firstName": "Lab", "lastName": "User", "email": email,
            "address": "10 Test Street", "city": "Belgorod", "pinCode": "308000",
        }.items():
            self.page.locator(f'input[name="{field}"]').fill(value)
        expect(self.page.get_by_text("$20", exact=True)).to_be_visible()
        self.page.get_by_role("button", name="Place Order", exact=True).click()

    def logout(self):
        self.page.get_by_role("button", name="Logout", exact=True).click()
        expect(self.page).to_have_url("/login")
