# MSWord Properties Generator

This repo will facilitate in generating a documents pair (MSWord and .pdf). based on an MSWord template with some parameters to provide.<br> 
The user can provide a Dropbox or Google Drive link to a signature image to include in the document. 

2 types of information needed to insert in the template document;   
  - Provider information:
    - Filling out a GitHub Actions form.<br>
    That information will be encrypted and stored in this repo for you to later use again.<br>
  - Customer information: 
    - Filling out a GitHub Actions form.<br>This will be the form that triggers the generation of the document pairs. (.docx and .pdf) 

At the moment of writing, depending of your choice, after the above actions this will result in:
- Sending a mail to the given e-mail address of the Provider with the generated documents. 
- Uploading the documents to the Dropbox of the owner of this repository.
- Customer data will not be stored. 
- Provider data *will* be stored in a separate private GitHub Repo, encrypted to protect your privacy.

## Resources 
- [res/Recht om te vertegenwoordigen.docx](res/Recht%20om%20te%20vertegenwoordigen.docx) MSWord template containing the Custom properties.
- [env/prod.properties](env/prod.properties) Properties for this logic to run containing all file names, folder locations. 

## ⚠️Dependencies⚠️
The following files found earlier in this repo that contained your encrypted data and signature image have moved to a private repo. \
That means, for proper working of this code we have a dependency to this private repo: 
- [msword-private-assets](https://github.com/johantre/msword-private-assets). As this is a private repo, the links below will show a 404. Serves as private vault for your sensitive data.
- [msword-signature-proxy](https://github.com/johantre/msword-signature-proxy). Cloudflare Worker acting as a proxy to avoid CORS issues when uploading signature images. 
- [msword-signature-loader](https://johantre.github.io/msword-signature-loader/) which is a helper page to upload your signature image. 

Still you are master of your data, and can always Subscribe/Unsubscribe found in section [Provider data](https://github.com/johantre/msword-properties-generator#Provider-data) to add/remove your data and signature image.

## Future enhancements
- some small code cleanups
- your suggestions are welcome!

## Usage
In order to have proper generated documents we need Provider and Customer data. Below how to do that.

### Provider data
Provider data doesn't change that much over time. Hence, since it's about quite some fields.<br>That data is stored in the [msword-private-assets](https://github.com/johantre/msword-private-assets) repo.<br> 
How to provide and update?
- GitHub Actions > Select **"Subscribe or Update provider"** workflow > **"Run workflow"** to add or update yourself as a Provider to the [msword-private-assets/res/offers_provider.db](https://github.com/johantre/msword-private-assets/blob/main/res/offers_provider.db).<br>
This process takes on average about 20 sec.
  - The last field you can provide an URL to Dropbox or Google Drive to a signature image.<br>Take into account a white background so it matches the background color of the document.
  <br><a href="assets/img_1.png"><img src="assets/img_1.png" width="300"></a><br> 
  - In order for this to work, you'll need to share an image with permissions to **"Anyone that has the link"**.<br>
    Once this process is done, you can remove that permission of your link again.<br>
  - 💡No Dropbox or Google Drive account at your disposal?💡\
  💡Head over to **https://johantre.github.io/msword-signature-loader/**!💡\
  💡This will help you take a snap of your signature with your smartphone right away and continue to the screen above, cropping, brightness and contrast adjustment included!!💡\
  💡Check out the [msword-signature-loader\README.md](https://github.com/johantre/msword-signature-loader/README.md) for a step-by-step explanation with screenshots.💡
  - All your data will be encrypted. That includes the image that'll be stored in the [msword-private-assets](https://github.com/johantre/msword-private-assets) repo under a hashed name to protect your privacy. 
- GitHub Actions > Select **"Unsubscribe provider"** workflow > **"Run workflow"** to remove your Provider data.<br>
This process takes on average about 20 sec.
  - All your Provider data will be removed, including the encrypted signature image file stored in the private repo: [msword-private-assets](https://github.com/johantre/msword-private-assets) 
  <br><a href="assets/img_2.png"><img src="assets/img_2.png" width="300"></a><br>

### Customer data
Customer data changes frequently.<br>Every time you need documents to be generated these parameters are different, and are only a few fields.<br> 
How to provide? 
- GitHub Actions > Select **"Generate, Send and add to Dropbox"** workflow > **"Run workflow"**<br>to generate the documents and have them send to the given mail.<br>
This process takes on average about 2 min.
  - Behind the scenes [Provider data](https://github.com/johantre/msword-properties-generator#Provider-data) will be picked up to consolidate in the generating of the document pair. (docx & pdf)<br>
  - So be aware that you'll need to have your Provider data in there as well for this to work.<br>Take into account Attention regarding the mail address.
  <br><a href="assets/img.png"><img src="assets/img.png" width="300"></a>

## ⚠️Attention⚠️

- The way this 2-way information flow has been set up is by means of the mail address as key to relate both information.<br>
So the mail address provided for the Customer and Provider information screen must be equal.<br>
Check out the 3 screenshots in this article; they *must be the same* in order for this to work! 
  - "Leverancier Mail" 

## Test Status

![Tests](https://github.com/johantre/msword-properties-generator/actions/workflows/tests.yml/badge.svg?branch=master)
[![Code Coverage](https://codecov.io/gh/johantre/msword-properties-generator/branch/master/graph/badge.svg)](https://app.codecov.io/gh/johantre/msword-properties-generator)



## Installation

```bash
pip install -e .
```

## Testing

Run the tests with:

```bash
pytest test/
```

For coverage report:

```bash
pytest --cov=msword_properties_generator test/
```

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0). This means you can:

- Share: Copy and redistribute the material in any medium or format
- Adapt: Remix, transform, and build upon the material

Under the following terms:
- Attribution: You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- NonCommercial: You may not use the material for commercial purposes.
- No additional restrictions: You may not apply legal terms or technological measures that legally restrict others from doing anything the license permits.

See the [LICENSE](LICENSE) file for details.

