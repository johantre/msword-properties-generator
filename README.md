# msword-properties-generator

This repo will generate MSWord document with filled out Custom properties and .pdf version of it from 
* 1 MSWord template document (containing Custom Properties, but filled with ****).
* 2 MSExcel workbooks containing the Custom Properties being the final values.([OffersCustomer.xlsx](res%2FOffersCustomer.xlsx), [OffersProvider.xlsx](res%2FOffersProvider.xlsx))
* Logs all your generated document Custom Properties. ([OffersLog.xlsx](res%2FOffersLog.xlsx))

## Usage 
* Edit your resources: ([OffersCustomer.xlsx](res%2FOffersCustomer.xlsx), [OffersProvider.xlsx](res%2FOffersProvider.xlsx)).  
  Main purpose is to only use the [OffersCustomer.xlsx](res%2FOffersCustomer.xlsx) to set the 3 most important fields,\
  and run the script afterwards to generate your .pdf and .docx.
* The main script in companion resources (xlsx, .docx, .properties) can be used as 
  * straight as script from within your development environment.
  * from an build pipeline when the edited resources are pushed.

## Resources 
[Recht om te vertegenwoordigen.docx](res%2FRecht%20om%20te%20vertegenwoordigen.docx) MSWord template containing the Custom properties.\
[OffersCustomer.xlsx](res%2FOffersCustomer.xlsx) Main xlsx that contains the Custom properties to set into the .docx file.\
[OffersProvider.xlsx](res%2FOffersProvider.xlsx) Main xlsx with the provider Custom properties\
[OffersLog.xlsx](res%2FOffersLog.xlsx) Log of all Custom properties sets used in the past\
[prod.properties](env%2Fprod.properties) Properties for this logic to run containing all file names, folder locations.

