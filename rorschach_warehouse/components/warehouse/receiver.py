from datetime import datetime, timezone
import pandas as pd
import time
from sqlalchemy import desc, not_
from sqlalchemy.sql import func
from os import getenv
from nite_howl import NiteHowl, minute
from db.base import Session
from models.snapshots.entity import Entity
from models.policies.statement import Statement
from models.providers.provider import Provider
from models.providers.source.source import Source
from models.snapshots.snapshot import SnapShot

class Receiver:
    def __init__(self):
        self.broker = getenv('BROKER')
        self.topic = getenv('TOPIC')
        self.group = getenv('GROUP')
        self.env =  getenv('ENV_PATH')
        self.howler = NiteHowl(self.broker, self.group, str(self.topic).split(","), "warehouse")
        
    def catch(self):
        radar_generator = self.howler.radar()

        while True:
            try:
                minute.register("info", f"Searching topics for warehouse...")
                msg, topic, key, headers, type = next(radar_generator)
                if key == "request":
                    if headers and "module" in headers.keys() and headers["module"] == "entity":
                        self.get_entity(key, headers, msg)
                else:
                    minute.register("info", f"That larva '{key}' won't need me.")
            except StopIteration:
                # Si radar_generator se agota, crea una nueva instancia
                radar_generator = self.howler.radar()
            # Pausa breve para no saturar el bucle
            time.sleep(0.1)
        
    def commit(self, csv, key, crm = pd.DataFrame([])):            
        for index, _ in csv.iterrows():
            left_row = csv.iloc[index]
            right_row = crm.iloc[index] if not crm.empty else {"ffm_subscriber_id": "", "salesorder_no": 0, "member_id": ""}
                       
            self.howler.send(
                'warehouse',
                msg = left_row == right_row,
                key = key,
                headers = { 
                    "group_id": [
                        left_row["ffm_subscriber_id"],
                        right_row['salesorder_no'],
                        left_row["member_id"],
                        left_row["ffm_app_id"],
                    ]
                }
            )
            
    def get_entity(self, key, headers, msg): 
        existing_snapshots = self.existing_snapshots()
        with Session() as session:
            for k, v in existing_snapshots.items():
                if key == tuple(msg.items()):
                    existing_statement_status = k[6]
                    existing_statement = session.query(Statement).filter_by(id=k[5]).scalar()
                    minute.register("info", f"Entity ID: {existing_statement.entity_id}")
                    break
            #self.howler.send("statement", existing_statement.entity_id, key=key, headers=headers)
            
    def existing_snapshots(self):
        with Session() as session:
            # Crear la subconsulta para obtener el timestamp máximo
            max_timestamp_subquery = (
                session.query(
                    Entity.id,
                    Entity.ffm_subscriber_id,
                    Entity.salesorder_no,
                    Entity.member_id,
                    Entity.ffm_app_id,
                    Statement.id.label('statement_id'),
                    SnapShot.timestamp,
                    SnapShot.status,
                    func.row_number().over(
                        partition_by=SnapShot.entity_id,
                        order_by=desc(SnapShot.id)
                    ).label('row_num')
                )
                .select_from(SnapShot)
                .join(Entity, Entity.id == SnapShot.entity_id)
                .join(Statement, Statement.entity_id == Entity.id)
                .subquery()
            )

            existing_snapshots = (
                session.query(
                    max_timestamp_subquery.c.ffm_subscriber_id,
                    max_timestamp_subquery.c.salesorder_no,
                    max_timestamp_subquery.c.member_id,
                    max_timestamp_subquery.c.ffm_app_id,
                    max_timestamp_subquery.c.id,
                    max_timestamp_subquery.c.statement_id,
                    max_timestamp_subquery.c.status,
                    max_timestamp_subquery.c.timestamp
                )
                .filter(max_timestamp_subquery.c.row_num == 1)
                .all()
            )
            # Retornar el resultado como un diccionario
            return {
                (t.ffm_subscriber_id, int(t.salesorder_no), t.member_id, t.ffm_app_id, t.id, t.statement_id, t.status): t.timestamp
                for t in existing_snapshots
            }
   
'''     def commit(self, csv, crm = pd.DataFrame([])): 
        with Session() as session:

            
            provider = None
            if source := session.query(Source).filter_by(name=self.provider_source).scalar():
                provider = session.query(Provider).filter_by(source=source.id).scalar()
            else:
                source = Source(
                    name = self.provider_source,
                    type = self.provider_source_type,
                )
                session.add(source)
                session.commit()
                provider = Provider(
                    name = self.provider_id,
                    type = self.provider_type,
                    source = source.id
                )
                session.add(provider)
                session.commit()
            
            for index, _ in csv.iterrows():
                left_row = csv.iloc[index]
                right_row = crm.iloc[index] if not crm.empty else {"ffm_subscriber_id": "", "salesorder_no": 0, "member_id": ""}
                
                changes = True
                existing_statement = False
                existing_statement_status = None

                key = (
                    left_row["ffm_subscriber_id"],
                    right_row['salesorder_no'],
                    left_row["member_id"],
                    left_row["ffm_app_id"],
                )
                
                for k, v in existing_snapshots.items():
                    if key == k[:4]:
                        existing_statement_status = k[6]
                        existing_statement = session.query(Statement).filter_by(id=k[5]).scalar()
                        break
                
                comparison_dict = {key: False for key in csv.keys()}
                if existing_statement:
                    policy_df = self.refactor_statement(existing_statement, csv.keys())
                    comparison_policy = policy_df == pd.Series(comparison_dict)
                    if all(comparison_policy):
                        changes = False
                
                if not crm.empty:
                    columns_to_ignore_empty_strings = ['member_id','ffm_subscriber_id']
                    columns_to_ignore_empty_integers = ['salesorder_no']
                    diff = (left_row == right_row)
                    
                    diff[columns_to_ignore_empty_strings] = diff[columns_to_ignore_empty_strings] & ~(left_row[columns_to_ignore_empty_strings].astype(str) == '')
                    diff[columns_to_ignore_empty_integers] = diff[columns_to_ignore_empty_integers] & ~(left_row[columns_to_ignore_empty_integers].astype(int) == 0)
                    
                    comparison_dict = diff

                    if existing_statement:
                        comparison_policy = policy_df == comparison_dict
                        if all(comparison_policy):
                            changes = False

                    statement = existing_statement
                else:
                    changes = True

                ##############################################################################################################
                """
pd.set_option('display.max_rows', 100)
pd.set_option('display.max_columns', 100)
diff_table = pd.concat(
    [
        left_row,
        right_row,
        diff
    ],
    axis=1,
    keys=["LEFT", "RIGHT", "DIFF"],
)
print(diff_table)
                """
                ##############################################################################################################

                if existing_statement:
                    entity = session.query(Entity).filter_by(id=existing_statement.entity_id).scalar()
                    if changes:
                        statement = self.create_statement(comparison_dict, session)
                        entity.statements.append(statement)
                else:
                    entity = Entity(
                        ffm_subscriber_id = key[0],
                        salesorder_no = key[1],
                        member_id = key[2],
                        ffm_app_id = key[3]
                    )
                    statement = self.create_statement(comparison_dict, session)
                    entity.statements.append(statement)

                session.add(entity)
                session.commit()

                snapshot = SnapShot(
                    entity_id = entity.id,
                    provider_id = provider.id,
                    timestamp = datetime.now(timezone.utc),
                    status = existing_statement_status if existing_statement_status and not changes else None,
                )
                
                entity.snapshots.append(snapshot)
                session.commit()
    

    def refactor_statement(self, existing_statement, columns):
        columns_to_drop = ['_sa_instance_state', 'id']  # Añadir cualquier otra columna que no sea necesaria
        policy_series = pd.DataFrame.from_dict(existing_statement.__dict__, orient='index').T
        policy_df = pd.DataFrame([])
        with Session() as session:
            unique = session.query(Unique).filter_by(id=existing_statement.unique_id).scalar()
            unique_series = pd.DataFrame.from_dict(unique.__dict__, orient='index').T
            unique_series = unique_series.drop(columns=columns_to_drop)

            basic = session.query(Basic).filter_by(id=existing_statement.basic_id).scalar()
            basic_series = pd.DataFrame.from_dict(basic.__dict__, orient='index').T
            basic_series = basic_series.drop(columns=columns_to_drop)

            auth = session.query(Auth).filter_by(id=existing_statement.auth_id).scalar()
            auth_series = pd.DataFrame.from_dict(auth.__dict__, orient='index').T
            auth_series = auth_series.drop(columns=columns_to_drop)

            detail = session.query(Detail).filter_by(id=existing_statement.detail_id).scalar()
            detail_series = pd.DataFrame.from_dict(detail.__dict__, orient='index').T
            detail_series = detail_series.drop(columns=columns_to_drop)

            address = session.query(Address).filter_by(id=existing_statement.address_id).scalar()
            address_series = pd.DataFrame.from_dict(address.__dict__, orient='index').T
            address_series = address_series.drop(columns=columns_to_drop)

            owner = session.query(Member).filter_by(group_id=existing_statement.group_id).filter_by(type_id=1).scalar()
            owner_series = pd.DataFrame.from_dict(owner.__dict__, orient='index').T
            owner_series = owner_series.drop(columns=columns_to_drop + ['type_id', 'group_id'])

            policy_series = pd.concat([unique_series, basic_series, auth_series, detail_series, address_series, owner_series], axis=1)
            
            spouse = session.query(Member).filter_by(group_id=existing_statement.group_id).filter_by(type_id=2).scalar()
            if spouse:
                spouse_series = pd.DataFrame.from_dict(spouse.__dict__, orient='index').T
                spouse_series = spouse_series.drop(columns=columns_to_drop + ['type_id', 'group_id'])
                spouse_series = spouse_series.rename(columns={
                    'first_name': 'spouse_first_name',
                    'last_name': 'spouse_last_name',
                    'ssn': 'spouse_ssn',
                    'gender': 'spouse_gender',
                    'dob': 'spouse_dob',
                    'applying': 'spouse_applying',
                })
                policy_series = pd.concat([policy_series, spouse_series], axis=1)

            others = session.query(Member).filter_by(group_id=existing_statement.group_id).filter(not_(Member.type_id.in_([1, 2]))).all()
            for other in others:
                other_series = pd.DataFrame.from_dict(other.__dict__, orient='index').T
                index = other.type_id
                other_series = other_series.drop(columns=columns_to_drop + ['type_id', 'group_id'])
                other_series = other_series.rename(columns={
                    'first_name': f'other_{index - 2}_first_name',
                    'last_name': f'other_{index - 2}_last_name',
                    'ssn': f'other_{index - 2}_ssn',
                    'gender': f'other_{index - 2}_gender',
                    'dob': f'other_{index - 2}_dob',
                    'applying': f'other_{index - 2}_applying',
                })
                policy_series = pd.concat([policy_series, other_series], axis=1)

        #policy_df = policy_series.drop(columns=columns_to_drop)
        policy_df = policy_series.reindex(columns=columns)
        with pd.option_context("future.no_silent_downcasting", True):
            policy_df = policy_df.fillna(True).infer_objects(copy=False)
        policy_df = policy_df.astype(bool)
        return policy_df.iloc[0]

    def create_statement(self, info: dict, session) -> Statement:
        unique = Unique(
            ffm_subscriber_id = info["ffm_subscriber_id"],
            salesorder_no = info["salesorder_no"],
            member_id = info["member_id"],
            ffm_app_id = info["ffm_app_id"],
        )

        basic = Basic(
            issuer = info["issuer"],
            effective_date = info["effective_date"],
            net_premium = info["net_premium"],
            policy_aor = info["policy_aor"],
            gross_premium = info["gross_premium"],
            plan_hios_id = info["plan_hios_id"],
            expiration_date = info["expiration_date"],
            policy_status = info["policy_status"],
            paid_through_date = info["paid_through_date"],
        )

        detail = Detail(
            last_date_doc = info["last_date_doc"],
            last_date_change = info["last_date_change"],
            out_of_pocket_max = info["out_of_pocket_max"],
            deductible = info["deductible"],
            followup_docs = info["followup_docs"],
            household_size = info["household_size"],
            household_income = info["household_income"],
            preferred_language = info["preferred_language"],
        )

        auth = Auth(
            user_mp = info["user_mp"],
            password_mp = info["password_mp"],
        )
        
        address = Address(
            address = info["address"],
            city = info["city"],
            state = info["state"],
            zip_code = info["zip_code"],
        )

        group = Group()

        owner = Member(
            group_id = group.id,
            first_name = info["first_name"],
            last_name = info["last_name"],
            ssn = info["ssn"],
            gender = info["gender"],
            dob = info["dob"],
            applying = info["applying"],
            type_id = 1
        )

        group.members.append(owner)

        spouse = Member(
            group_id = group.id,
            first_name = info["spouse_first_name"],
            last_name = info["spouse_last_name"],
            ssn = info["spouse_ssn"],
            gender = info["spouse_gender"],
            dob = info["spouse_dob"],
            applying = info["spouse_applying"],
            type_id = 2
        )
        group.members.append(spouse)
        
        other_1 = Member(
            group_id = group.id,
            first_name = info["other_1_first_name"],
            last_name = info["other_1_last_name"],
            ssn = info["other_1_ssn"],
            gender = info["other_1_gender"],
            dob = info["other_1_dob"],
            applying = info["other_1_applying"],
            type_id = 3
        )
        group.members.append(other_1)

        other_2 = Member(
            group_id = group.id,
            first_name = info["other_2_first_name"],
            last_name = info["other_2_last_name"],
            ssn = info["other_2_ssn"],
            gender = info["other_2_gender"],
            dob = info["other_2_dob"],
            applying = info["other_2_applying"],
            type_id = 4
        )
        group.members.append(other_2)

        other_3 = Member(
            group_id = group.id,
            first_name = info["other_3_first_name"],
            last_name = info["other_3_last_name"],
            ssn = info["other_3_ssn"],
            gender = info["other_3_gender"],
            dob = info["other_3_dob"],
            applying = info["other_3_applying"],
            type_id = 5
        )
        group.members.append(other_3)

        other_4 = Member(
            group_id = group.id,
            first_name = info["other_4_first_name"],
            last_name = info["other_4_last_name"],
            ssn = info["other_4_ssn"],
            gender = info["other_4_gender"],
            dob = info["other_4_dob"],
            applying = info["other_4_applying"],
            type_id = 6
        )
        group.members.append(other_4)

        other_5 = Member(
            group_id = group.id,
            first_name = info["other_5_first_name"],
            last_name = info["other_5_last_name"],
            ssn = info["other_5_ssn"],
            gender = info["other_5_gender"],
            dob = info["other_5_dob"],
            applying = info["other_5_applying"],
            type_id = 7
        )
        group.members.append(other_5)

        
        session.add(unique)
        session.add(basic)
        session.add(detail)
        session.add(auth)
        session.add(address)
        session.add(group)
        session.commit()

        statement = Statement(
            unique_id = unique.id,
            basic_id = basic.id,
            auth_id = auth.id,
            detail_id = detail.id,
            address_id = address.id,
            group_id = group.id,
        )

        return statement

     '''