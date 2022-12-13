### To add a parameter to Evolve Single Binary form
#### Django Server side
- Add field to Django model `SingleBinaryJob` in `src/compasui/models.py`
- To add the parameter to the Grid file that is passed to COMPAS
  * In `src/compasui/utils/constants.py`, map field name to a COMPAS parameter in `SINGLE_BINARY_FIELD_COMMANDS` dictionary
- `makemigrations` and `migrate`
- Modify the view that maps inputs to model fields and saves the model `create_single_binary_job` in 
`src/compasui/views`
  * add field to method signature
  * Add field to model constructor `single_binary_job = SingleBinaryJob(...)`
- In GraphQL schema `src/compasui/schema.py`, `SingleBinaryJobMutation` class:
  * define field in `Input` class
  * In `mutate_and_get_payload` method where graphql inputs are mapped to model parameters, add the field to 
`create_single_binary_job` view call, `job = create_single_binary_job(...)`
- Rebuild schema

#### React side
- **Note: field names used in the client side are the GraphQL schema names not the django model names.**
**Schema names are basically model names in camelCase, i.e. `common_envelope_lambda` in model becomes 
`commonEnvelopeLambda`**
- Add the field to one of the form components in `src/react/src/Components/Forms`. Field name in the react component 
 should be the field name in the schema
- Add parameter default value to `initialValues` in `src/react/src/Components/Forms/initialValues.js`
- Update validation schema with any required validations in `src/react/src/Components/Forms/validationSchema.js`
- Modify `NewSingleBinaryJob.js` page component in `src/react/src/Components/Pages/NewSingleBinaryJob.js`. 
Modify `variables` object in `handleJobSubmission` method to pass the new field to the graphql schema input