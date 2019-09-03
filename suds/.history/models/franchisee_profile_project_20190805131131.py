from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class FranchiseeProfile(models.Model):
    _inherit = 'project.project'

    #personal information
    date_of_birth = fields.Date(string="Date of Birth")
    age = fields.Integer(string="Age")
    gender = fields.Selection(selection=[
        ('female', 'Female'),
        ('male', 'Male')
        ],string="Gender")
    address = fields.Char(string="Address")
    years_living_in_address = fields.Float(string="Years Living in the Address")
    marital_status = fields.Selection(selection=[
        ('single', 'Single'),
        ('married', 'Married')
        
    ], string="Marital Status")
    children_ids = fields.One2many('children.info', 'project_id',string="Children")
    educ_course = fields.Char(string="Course Taken")
    educ_school = fields.Char(string="Schools Attended")
    employment_ids = fields.One2many('employment.info','project_id', string="Employment Information")
    home_phone_number = fields.Char(string="Home Phone Number")
    mobile_phone_number = fields.Char(string="Mobile Phone Number")
    email_address = fields.Char(string="Email Address")
    feedback = fields.Text(string="How did you hear about SUDS?")

    #questionnaire
    discussion_of_going_into_business = fields.Boolean(string="Have you and your spouse/partner thoroughly discussed the idea of going into business?")
    complete_agreement = fields.Boolean(string="Are you in complete agreement?")
    past_experience_business = fields.Boolean(string="Have you had past experience in running a business? If yes, please list specifics")
    previous_business_ids = fields.One2many('previous.business','project_id',string="Previous Business")
    own_current_business = fields.Boolean(string="Do you currently own a business? If yes, please list down Name and Type of business")
    current_business_ids = fields.One2many('current.business','project_id',string="Current Business/es")
    advantage_of_franchise = fields.Boolean(string="Are you prepared to give up independence of action in exchange for advantages that a franchised business can offer?")
    experience_handling_service_related_business = fields.Boolean(string="Have you had experience handling service-related work either in business or employment? Please list down specifics.")
    service_related_ids = fields.One2many('service.related','project_id', string="Service Related")
    experience_handling_org = fields.Boolean(string="Have you had experience handling staff/subordinates/ an organization?")
    organization_ids = fields.One2many('experience.organization','project_id',string="Organization/Experience")

    #financial information
    annual_income_ids = fields.One2many('annual.income', 'project_id', string="Annual Income")
    partner_annual_income_ids = fields.One2many('annual.income', 'project_id', string="Partner/Spouse Annual Income")
    current_residence = fields.Selection(selection=[
        ('owned', 'Owned'),
        ('rented', 'Rented'),
        ('mortgaged', 'Mortgaged')
    ])

    
    #questionnaire # 2
    savings_to_cushion_franchise = fields.Boolean(string="Will your savings be able provide you with a cushion of at least 1 year while you are starting up your franchise business?")
    spouse_employment = fields.Boolean(string="Will either you or your spouse remain employed while the franchise is in the initial stage?")
    focused_franchise = fields.Boolean(string="Will either you or your spouse be focused on your Suds franchise?")
    reason_for_not_focused = fields.Char(string="If not, who will be running the franchise operations?")
    sole_source_income = fields.Boolean(string="Will this business be your sole source of income?")
    partners_for_franchise = fields.Boolean(sttring="Will you have partners in this franchise?")
    franchise_partner_names = fields.Char(string="If yes, who?")
    finance_investment = fields.Boolean(string="Will you be financing the investment in this franchise?")
    investment_amount = fields.Float(string="If yes, where and how much do you plan to obtain financing?")

    #franchise management information
    personally_manage_store = fields.Boolean(string="Will you be personally managing your Suds store/s?")
    not_manage_relationship = fields.Char(string="If not, who will manage your store and what is his/her relationship to you?")
    educational_attainment_manager = fields.Char(string="What is the educational attainment of your manager?")
    spend_six_hours_per_week = fields.Boolean(string="Will you or your manager be able to spend at least 6 hours per week on your Suds business?")

    #specific operations
    start_franchise_business = fields.Datetime(string="If approved, when can you be ready to start your franchise business (Month/Year)?")
    area_location_suds_franchise = fields.Char(string="Which specific area/city/municipality do you plan to put up your Suds Franchise?")
    proposed_location = fields.Boolean(string="Do you have a proposed location ready?")
    frontage_dimension_sqm = fields.Float(string="Dimensions in square meters:")
    length_dimension_sqm = fields.Float(string="Dimensions in square meters:")
    parking_available = fields.Boolean(string="Is Parking Available?")
    floor_level = fields.Integer(string="Floor/ Level of location (Ground floor is preferred if no elevator is available)")
    owner_of_proposed_location = fields.Selection(selection=[
        ('franchise_owned', 'Franchise Owned'),
        ('landlord', 'Landlord')
    ],string="Owner of Proposed Location")
    contractual_obligations = fields.Text(string="Do you have existing contractual obligations or litigations that may affect/hinder/limit your participation in a Suds franchise operations?")
    qualities_possesed_to_franchise_suds = fields.Text(string="What are the qualities you possess that make you suited to be a Suds franchisee?")
    persistence_business = fields.Text(string="Do you think you have the persistence and drive to manage a business? Why?")
    take_charge_business_problem = fields.Text(string="Are you able to take charge in taking care of business problems that may come up?")
    other_details_suds_need_to_know = fields.Text(string="Are there other details you want Suds to know?")

class AnnualIncome(models.Model):
    _name='annual.income'

    project_id = fields.Many2one('project.project')
    income_source = fields.Char(string="Source")
    income_amount = fields.Float(string="Amount")



class ChildrenInfo(models.Model):
    _name='children.info'

    project_id = fields.Many2one('project.project')
    child_name = fields.Char(string="Name")
    age = fields.Integer(string="Age")

class EmploymentInformation(models.Model):
    _name='employment.info'

    project_id = fields.Many2one('project.project')
    company_name = fields.Char(string="Company Name")
    position_held = fields.Char(string="Position")

class PreviousBusiness(models.Model):
    _name='previous.business'

    project_id = fields.Many2one('project.project')
    business_name = fields.Char(string="Business Name")
    business_type = fields.Char(string="Business Type")

class CurrentBusiness(models.Model):
    _name='current.business'

    project_id = fields.Many2one('project.project')
    business_name = fields.Char(string="Business Name")
    business_type = fields.Char(string="Business Type")

class CurrentBusiness(models.Model):
    _name='service.related'

    project_id = fields.Many2one('project.project')
    service_related_work = fields.Char(string="Service Related Work")
    description = fields.Char(string="Description")

class OrganizationExperience(models.Model):
    _name='experience.organization'

    project_id = fields.Many2one('project.project')
    experience = fields.Char(string="Experience")
    number_people_handled = fields.Integer(string="Number of People Handled")

