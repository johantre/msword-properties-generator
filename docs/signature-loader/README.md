# MSWord Signature Loader

This README.md is part of the [msword-properties-generator](https://github.com/johantre/msword-properties-generator) and explains how to upload your signature image to the private repo [msword-private-assets](https://github.com/johantre/msword-private-assets) in case one does not have an image download link available on Dropbox or Google Drive. 

## Some background
Under the hood, instead of Dropbox or Google Drive, the services of [Uguu.se](https://uguu.se/) are being used to provide a download link in the workflow to store on Provider data in the private repo [msword-private-assets](https://github.com/johantre/msword-private-assets)\
[Uguu](https://uguu.se/) is a service that 
- doesn't need an account, 
- stores your image for 3 hours of time 
- removes your image after that period of 3 hours.
- has API support
- The link [Uguu](https://uguu.se/) returns is only seen to you, and unless you pass that link to others, it stays only known by you. 

"Why not directly committing & pushing to that private repo? Why using a step in between?" you might ask.\
That would leave quite a few problems unresolved:
- The permissions to repo where the images are stored would have to be managed, which isn't sustainable.
- Privacy: it would be possible to download all images stored, even though they are encrypted and stored with a hashed file name.
- The encryption would have to be done client side, which leaves too much complexity for the user.
- We don't want to leave any traces in the repo of the unencrypted image. The only version in the private repo can be the encrypted version.

## Usage 
This helper is part if this repo and hosted through GitHub Pages. All you need is the link to get started.\
It can be used through desktop or mobile. Most handy is mobile, as this offers you the means of taking a snap and work with that directly.\
Below is a step-by-step guide on mobile to illustrate. 

**https://johantre.github.io/msword-properties-generator/signature-loader/**

### Snap and adjust
- On mobile, clicking the "Choose file" button opens up the camera app so you can take a snap of your signature.\
Then adjust cropping, contrast and brightness to make your signature match with the background of the document it will be placed.
- Click "Crop" at the bottom, and 
- Click "Upload" so have the link copied to your clipboard.\
In case you copied something else and lost the download [Uguu](https://uguu.se/) link from your clipboard, you have a "Copy link again" button.
- Click the "Open GitHub Actions form" button to start the workflow of filling out the Provider data, including copy pasting the [Uguu](https://uguu.se/) download link. 
<div style="display: flex; justify-content: space-between;">
<a href="../../assets/signature-loader/Signature Loader1.png"><img src="../../assets/signature-loader/Signature Loader1.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader2.png"><img src="../../assets/signature-loader/Signature Loader2.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader3.png"><img src="../../assets/signature-loader/Signature Loader3.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader4.png"><img src="../../assets/signature-loader/Signature Loader4.png" width="200"></a>
</div>

### Using the link
If you clicked "Open GitHub Actions form" you'll see the first screen. ⚠️ Notice ⚠️ you'll need a GitHub account in order to start this workflow!\
- Here you click the "Run workflow" button. (which won't be available if you didn't log in)\
You'll see the input screen (same as explained in [msword-properties-generator](https://github.com/johantre/msword-properties-generator) README.md)\
- On mobile, long-press the signature field at the bottom of the form, to paste your [Uguu](https://uguu.se/) link from your clipboard.
- Fill out the other Provider data fields
- Hit "Run workflow" at the bottom to persist your Provider data to the private repo.\
Not sure what to fill out there?  Check out the template document [Recht om te vertegenwoordigen.docx](../../res/Recht om te vertegenwoordigen.docx) in this repo for some guidance. The fields are named so know what data to fill out where. 
<div style="display: flex; justify-content: space-between;">
<a href="../../assets/signature-loader/Signature Loader5.png"><img src="../../assets/signature-loader/Signature Loader5.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader6.png"><img src="../../assets/signature-loader/Signature Loader6.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader7.png"><img src="../../assets/signature-loader/Signature Loader7.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader8.png"><img src="../../assets/signature-loader/Signature Loader8.png" width="200"></a>
</div>

### Using together with Customer data
Above, we filled out the Provider data.  Below we'll fill out the Customer data and generate the goodies we're after.\
See [msword-properties-generator](https://github.com/johantre/msword-properties-generator) README.md for more info.

Once the above workflow did run, your screen will look like the first screen below.\
We'll need to run another workflow to generate the document pair with all the filled out data.
- Click the workflow selector on top
- Select "Generate, Send & add to Dropbox"
- Fill out the Customer data
- Fill out the Provider mail again, ⚠️the same as in the Provider workflow⚠️
- Hit the "Run workflow" at the bottom 

<div style="display: flex; justify-content: space-between;">
<a href="../../assets/signature-loader/Usage1.png"><img src="../../assets/signature-loader/Usage1.png" width="200"></a>
<a href="../../assets/signature-loader/Usage2.png"><img src="../../assets/signature-loader/Usage2.png" width="200"></a>
<a href="../../assets/signature-loader/Usage3.png"><img src="../../assets/signature-loader/Usage3.png" width="200"></a>
<a href="../../assets/signature-loader/Usage4.png"><img src="../../assets/signature-loader/Usage4.png" width="200"></a>
</div>

### The result 
Below what'll be the result of using your Provider data, like the signature download link.

- If you clicked "Run workflow" you'll see the first screen below. That means your workflow is running.  
- Providing you selected to recieve a mail, you'll see a mail as in the second screen.
- Lo and behold; opening up the pdf shows the signature as provided in the first step in this README.md

<div style="display: flex; justify-content: space-between;">
<a href="../../assets/signature-loader/Signature Loader-GenerateSend1.png"><img src="../../assets/signature-loader/Signature Loader-GenerateSend1.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader-GenerateSend2.png"><img src="../../assets/signature-loader/Signature Loader-GenerateSend2.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader-GenerateSend3.png"><img src="../../assets/signature-loader/Signature Loader-GenerateSend3.png" width="200"></a>
<a href="../../assets/signature-loader/Signature Loader-GenerateSend4.png"><img src="../../assets/signature-loader/Signature Loader-GenerateSend4.png" width="200"></a>
</div>

## ⚠️ Dependencies ⚠️
Below, everything what's under the hood.
- [Uguu.se](https://uguu.se/)
- Cloudflare Worker script to assure requests to [Uguu.se](https://uguu.se/) are done with the sufficient headers.\
That is achieved by a Cloudflare Worker script [msword-signature-proxy](https://github.com/johantre/msword-signature-proxy) that needs to be deployed in Cloudflare. 

