import re

with open(r'app/templates/home.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''      <div class="footerColumn">
        <h4>Brand</h4>
        <ul class="footerList">
          <li>Why Natural Products?</li>
          <li>The Flor\u2019avis Difference</li>
          <li>No Harmful Ingredients</li>
        </ul>
      </div>

      <div class="footerColumn">
        <h4>Shop</h4>
        <ul class="footerList">
          <li>Block soap</li>
          <li>Best seller</li>
          <li>Bundles</li>
          <li>Announcements</li>
        </ul>
      </div>

      <div class="footerColumn">
        <h4>Support</h4>
        <ul class="footerList">
          <li>FAQ</li>
          <li>Contact us</li>
          <li>Store Policies</li>
          <li>Shipping Policy</li>
        </ul>
      </div>'''

new = '''      <div class="footerColumn">
        <h4>Brand</h4>
        <ul class="footerList">
          <li><a href="{{ url_for('about_us') }}">Why Natural Products?</a></li>
          <li><a href="{{ url_for('about_us') }}">The Flor\u2019avis Difference</a></li>
          <li><a href="{{ url_for('about_us') }}">No Harmful Ingredients</a></li>
        </ul>
      </div>

      <div class="footerColumn">
        <h4>Shop</h4>
        <ul class="footerList">
          <li><a href="{{ url_for('shop', category='classic') }}">Block Soap</a></li>
          <li><a href="{{ url_for('shop') }}">Best Seller</a></li>
          <li><a href="{{ url_for('shop', category='luxury') }}">Bundles</a></li>
          <li><a href="{{ url_for('home') }}">Announcements</a></li>
        </ul>
      </div>

      <div class="footerColumn">
        <h4>Support</h4>
        <ul class="footerList">
          <li><a href="{{ url_for('about_us') }}">FAQ</a></li>
          <li><a href="{{ url_for('contact') }}">Contact Us</a></li>
          <li><a href="{{ url_for('about_us') }}">Store Policies</a></li>
          <li><a href="{{ url_for('about_us') }}">Shipping Policy</a></li>
        </ul>
      </div>'''

if old in content:
    content = content.replace(old, new)
    with open(r'app/templates/home.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('OK - footer links updated')
else:
    print('NOT FOUND')
